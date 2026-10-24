"""Conservative, local-only CSV cleanup for small client-approved datasets.

The tool never uploads data, guesses missing values, or edits the input file.
Duplicate rules must be agreed with the client and supplied with --key-columns
when the full row is not a safe identity rule.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable


class CleanupError(ValueError):
    """Raised when the CSV shape or requested cleanup rules are unsafe."""


def _cell(value: object) -> str:
    return "" if value is None else str(value).strip()


def _signature(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(value.casefold() for value in values)


def _resolve_columns(headers: list[str], requested: list[str] | None, label: str) -> list[int]:
    lookup = {name.casefold(): index for index, name in enumerate(headers)}
    names = [_cell(name) for name in (requested or [])]
    folded = [name.casefold() for name in names]
    if len(set(folded)) != len(folded):
        raise CleanupError(f"{label} columns must be unique.")
    missing = [name for name in names if name.casefold() not in lookup]
    if missing:
        raise CleanupError(f"Unknown {label} column(s): " + ", ".join(missing))
    return [lookup[name.casefold()] for name in names]


def _normalize_email(value: str) -> tuple[str, str | None]:
    """Normalize only the domain case; preserve the potentially case-sensitive local part."""
    if value.count("@") != 1 or any(character.isspace() for character in value):
        return value, "invalid_email_format"
    local, domain = value.split("@", 1)
    if not local or not domain:
        return value, "invalid_email_format"
    return f"{local}@{domain.casefold()}", None


def _normalize_phone(value: str) -> tuple[str, str | None]:
    """Remove visual separators without guessing a country code or dropping digits."""
    compact = re.sub(r"[\s().-]", "", value)
    if not compact:
        return compact, None
    digits = compact[1:] if compact.startswith("+") else compact
    if not digits.isdigit() or not 7 <= len(digits) <= 15:
        return value, "invalid_phone_format"
    return compact, None


def clean_rows(
    headers: list[str],
    records: list[list[str]],
    key_columns: list[str] | None = None,
    email_columns: list[str] | None = None,
    phone_columns: list[str] | None = None,
) -> tuple[list[str], list[list[str]], list[list[str]]]:
    """Trim cell edges and return (headers, kept rows, auditable exceptions).

    With explicit keys, rows sharing a complete key are compared across all
    columns. Repeated rows keep the first record; disagreements quarantine all
    rows in that key group instead of choosing a winner. Rows with missing key
    values are also quarantined. Without keys, only exact rows after trimming
    are deduplicated. Optional email/phone normalization is deliberately narrow;
    malformed selected values are quarantined for review.
    """
    cleaned_headers = [_cell(name) for name in headers]
    if not cleaned_headers or any(not name for name in cleaned_headers):
        raise CleanupError("CSV must have a header row with no blank column names.")
    folded_headers = [name.casefold() for name in cleaned_headers]
    if len(set(folded_headers)) != len(folded_headers):
        raise CleanupError("CSV has duplicate column names after trimming/case-folding.")
    if {"_apip_source_record", "_apip_issue"}.intersection(folded_headers):
        raise CleanupError("Input uses reserved APIP exception column names.")

    key_indexes = _resolve_columns(cleaned_headers, key_columns, "Key")
    email_indexes = _resolve_columns(cleaned_headers, email_columns, "Email")
    phone_indexes = _resolve_columns(cleaned_headers, phone_columns, "Phone")
    if set(email_indexes).intersection(phone_indexes):
        raise CleanupError("A column cannot be selected as both email and phone.")
    keys = [cleaned_headers[index] for index in key_indexes]

    normalized: list[tuple[int, list[str], list[str]]] = []
    for record_number, row in enumerate(records, start=2):
        if len(row) != len(cleaned_headers):
            raise CleanupError(
                f"Record {record_number} has {len(row)} values; expected {len(cleaned_headers)}."
            )
        values = [_cell(value) for value in row]
        trimmed_values = values.copy()
        issues: list[str] = []
        for index in email_indexes:
            if values[index]:
                values[index], issue = _normalize_email(values[index])
                if issue:
                    issues.append(f"{issue}:{cleaned_headers[index]}")
        for index in phone_indexes:
            if values[index]:
                values[index], issue = _normalize_phone(values[index])
                if issue:
                    issues.append(f"{issue}:{cleaned_headers[index]}")
        if issues:
            values = trimmed_values
        normalized.append((record_number, values, issues))

    kept: list[list[str]] = []
    exceptions: list[list[str]] = []
    if not keys:
        seen: set[tuple[str, ...]] = set()
        for record_number, values, issues in normalized:
            if issues:
                exceptions.append([str(record_number), ";".join(issues), *values])
                continue
            sig = tuple(values)
            if not any(values):
                issue = "empty_row"
            elif sig in seen:
                issue = "duplicate_exact_row"
            else:
                seen.add(sig)
                kept.append(values)
                continue
            exceptions.append([str(record_number), issue, *values])
        return cleaned_headers, kept, exceptions

    groups: dict[tuple[str, ...], list[tuple[int, list[str]]]] = defaultdict(list)
    for record_number, values, issues in normalized:
        if issues:
            exceptions.append([str(record_number), ";".join(issues), *values])
            continue
        if not any(values):
            exceptions.append([str(record_number), "empty_row", *values])
            continue
        key_values = [values[cleaned_headers.index(key)] for key in keys]
        empty_keys = [key for key, value in zip(keys, key_values) if not value]
        if empty_keys:
            exceptions.append([
                str(record_number),
                "missing_key_value:" + ",".join(empty_keys),
                *values,
            ])
            continue
        groups[_signature(key_values)].append((record_number, values))

    for group in groups.values():
        # Duplicate removal is exact and case-sensitive after trimming. Keys
        # are case-folded only to surface possible collisions for review.
        signatures = {tuple(values) for _, values in group}
        if len(signatures) > 1:
            changed_columns = [
                header
                for index, header in enumerate(cleaned_headers)
                if len({values[index] for _, values in group}) > 1
            ]
            issue = "conflicting_key_values:" + ",".join(changed_columns)
            for record_number, values in group:
                exceptions.append([str(record_number), issue, *values])
            continue

        first_record, first_values = group[0]
        kept.append(first_values)
        for record_number, values in group[1:]:
            exceptions.append([str(record_number), "duplicate_exact_after_trim", *values])

    exceptions.sort(key=lambda row: int(row[0]))
    return cleaned_headers, kept, exceptions


def read_csv(path: Path, max_records: int) -> tuple[list[str], list[list[str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            try:
                headers = next(reader)
            except StopIteration:
                raise CleanupError("Input CSV is empty.") from None
            records: list[list[str]] = []
            for row in reader:
                if len(records) >= max_records:
                    raise CleanupError(f"Input exceeds the configured {max_records} record limit.")
                records.append(row)
            return headers, records
    except UnicodeDecodeError:
        raise CleanupError("Input must be a UTF-8 CSV file.") from None
    except csv.Error as exc:
        raise CleanupError(f"CSV parsing failed: {exc}") from None


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(headers)
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        return temporary
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _mapping_guide_rows(
    headers: list[str],
    target_fields: list[str] | None,
    field_map: list[str] | None,
    email_columns: list[str] | None,
    phone_columns: list[str] | None,
) -> list[list[str]]:
    source_lookup = {name.casefold(): name for name in headers}
    email_names = {name.casefold() for name in (email_columns or [])}
    phone_names = {name.casefold() for name in (phone_columns or [])}
    mappings: dict[str, str] = {}
    mapped_targets: set[str] = set()
    for raw_mapping in field_map or []:
        if "=" not in raw_mapping:
            raise CleanupError("Field mappings must use SOURCE=TARGET format.")
        source_name, target_name = (_cell(part) for part in raw_mapping.split("=", 1))
        if not source_name or not target_name:
            raise CleanupError("Field mappings must include both a source and target.")
        source_key = source_name.casefold()
        target_key = target_name.casefold()
        if source_key not in source_lookup:
            raise CleanupError(f"Unknown field-map source column: {source_name}")
        if source_key in mappings:
            raise CleanupError(f"Source column mapped more than once: {source_name}")
        if target_key in mapped_targets:
            raise CleanupError(f"Target field mapped more than once: {target_name}")
        mappings[source_key] = target_name
        mapped_targets.add(target_key)

    targets = [_cell(name) for name in (target_fields or [])]
    if any(not name for name in targets) or len({name.casefold() for name in targets}) != len(targets):
        raise CleanupError("Target fields must be nonblank and unique.")
    target_lookup = {name.casefold(): name for name in targets}
    unknown_targets = [name for name in mappings.values() if targets and name.casefold() not in target_lookup]
    if unknown_targets:
        raise CleanupError("Mapped target field(s) missing from --target-fields: " + ", ".join(unknown_targets))

    rows: list[list[str]] = []
    for source in headers:
        if source.casefold() in email_names:
            handling = "Trim; lowercase domain only; preserve local part; malformed values go to review"
        elif source.casefold() in phone_names:
            handling = "Trim; remove visual separators; preserve digits and leading +; no country-code inference"
        else:
            handling = "Trim outer whitespace only; preserve other values"
        mapped = mappings.get(source.casefold(), "")
        status = "proposed mapping; buyer confirmation required" if mapped else "target field needs buyer mapping"
        rows.append([source, mapped, handling, status])

    for target in targets:
        if target.casefold() not in mapped_targets:
            rows.append([
                "",
                target,
                "No source column supplied; ask buyer how to populate",
                "missing source; buyer decision required",
            ])
    return rows


def process_file(
    input_path: Path,
    output_dir: Path,
    key_columns: list[str] | None = None,
    max_records: int = 10000,
    force: bool = False,
    email_columns: list[str] | None = None,
    phone_columns: list[str] | None = None,
    target_fields: list[str] | None = None,
    field_map: list[str] | None = None,
) -> tuple[Path, Path, dict[str, int]]:
    if max_records < 1:
        raise CleanupError("Record limit must be positive.")
    source = input_path.resolve(strict=True)
    if not source.is_file():
        raise CleanupError("Input path must be a file.")
    headers, records = read_csv(source, max_records)
    headers, kept, exceptions = clean_rows(
        headers,
        records,
        key_columns,
        email_columns=email_columns,
        phone_columns=phone_columns,
    )
    mapping_rows = _mapping_guide_rows(
        headers,
        target_fields=target_fields,
        field_map=field_map,
        email_columns=email_columns,
        phone_columns=phone_columns,
    )

    destination = output_dir.resolve()
    cleaned_path = destination / f"cleaned-{source.stem}.csv"
    exceptions_path = destination / f"exceptions-{source.stem}.csv"
    mapping_path = destination / f"mapping-guide-{source.stem}.csv"
    if cleaned_path == source or exceptions_path == source or mapping_path == source:
        raise CleanupError("Output path cannot overwrite the input file.")
    existing = [path for path in (cleaned_path, exceptions_path, mapping_path) if path.exists()]
    if existing and not force:
        raise CleanupError("Output already exists; choose another folder or pass --force to replace it.")

    exception_headers = ["_apip_source_record", "_apip_issue", *headers]
    temporary_files: list[Path] = []
    try:
        temporary_files.append(_write_csv(cleaned_path, headers, kept))
        temporary_files.append(_write_csv(exceptions_path, exception_headers, exceptions))
        temporary_files.append(_write_csv(
            mapping_path,
            ["source_column", "target_field", "handling", "mapping_status"],
            mapping_rows,
        ))
        os.replace(temporary_files[0], cleaned_path)
        temporary_files.pop(0)
        os.replace(temporary_files[0], exceptions_path)
        temporary_files.pop(0)
        os.replace(temporary_files[0], mapping_path)
        temporary_files.clear()
    finally:
        for temporary in temporary_files:
            temporary.unlink(missing_ok=True)

    stats = {
        "input_records": len(records),
        "cleaned_records": len(kept),
        "exception_records": len(exceptions),
        "duplicates_removed": sum(
            row[1].startswith("duplicate_") for row in exceptions
        ),
    }
    return cleaned_path, exceptions_path, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--key-columns", nargs="+", help="Client-approved duplicate identity columns")
    parser.add_argument("--email-columns", nargs="+", help="Opt in to conservative email domain normalization")
    parser.add_argument("--phone-columns", nargs="+", help="Opt in to separator removal; no locale inference")
    parser.add_argument("--target-fields", nargs="+", help="Buyer-provided destination fields for the mapping guide")
    parser.add_argument("--field-map", action="append", help="Proposed SOURCE=TARGET mapping; buyer confirmation is still required")
    parser.add_argument("--max-records", type=int, default=10000)
    parser.add_argument("--force", action="store_true", help="Replace matching output files")
    args = parser.parse_args(argv)
    output_dir = args.output_dir or args.input_csv.parent / f"{args.input_csv.stem}-apip-output"
    try:
        cleaned, exceptions, stats = process_file(
            args.input_csv,
            output_dir,
            key_columns=args.key_columns,
            max_records=args.max_records,
            force=args.force,
            email_columns=args.email_columns,
            phone_columns=args.phone_columns,
            target_fields=args.target_fields,
            field_map=args.field_map,
        )
    except (CleanupError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        "Processed {input_records} records: {cleaned_records} kept, "
        "{exception_records} exceptions, {duplicates_removed} duplicates removed.".format(**stats)
    )
    print(f"Cleaned output: {cleaned}")
    print(f"Exceptions output: {exceptions}")
    print(f"Field-mapping guide: {cleaned.parent / f'mapping-guide-{args.input_csv.stem}.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
