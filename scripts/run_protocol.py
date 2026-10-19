
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal, InvalidOperation

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "income-ledger.csv"
REPORTS = ROOT / "reports"
STATE = ROOT / "PROJECT_STATE.md"
TASKS = ROOT / "TASKS.md"

FIELDS = [
    "record_id", "date_utc", "experiment_id", "event_type", "status",
    "currency", "gross_amount", "fees", "refunds", "other_costs",
    "net_amount", "amount_received", "proof_url", "notes"
]

MONEY_FIELDS = [
    "gross_amount", "fees", "refunds", "other_costs",
    "net_amount", "amount_received"
]


def check_ledger():
    errors = []
    records = []

    if not LEDGER.exists():
        return ["Missing data/income-ledger.csv"], records

    with LEDGER.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDS:
            return ["Ledger header does not match the required schema."], records

        seen_ids = set()

        for line, row in enumerate(reader, start=2):
            if not any((value or "").strip() for value in row.values()):
                continue

            record_id = (row.get("record_id") or "").strip()
            if not record_id:
                errors.append(f"Line {line}: record_id is required.")
            elif record_id in seen_ids:
                errors.append(f"Line {line}: duplicate record_id {record_id}.")
            seen_ids.add(record_id)

            try:
                datetime.strptime(row["date_utc"], "%Y-%m-%d")
            except (ValueError, TypeError):
                errors.append(f"Line {line}: date_utc must use YYYY-MM-DD.")

            for field in MONEY_FIELDS:
                try:
                    amount = Decimal(row[field])
                    if not amount.is_finite() or amount < 0:
                        raise InvalidOperation
                except (InvalidOperation, TypeError, KeyError):
                    errors.append(
                        f"Line {line}: {field} must be a non-negative number."
                    )

            try:
                gross = Decimal(row["gross_amount"])
                fees = Decimal(row["fees"])
                refunds = Decimal(row["refunds"])
                costs = Decimal(row["other_costs"])
                net = Decimal(row["net_amount"])
                received = Decimal(row["amount_received"])

                if net != gross - fees - refunds - costs:
                    errors.append(
                        f"Line {line}: net_amount must equal gross minus "
                        "fees, refunds, and other_costs."
                    )

                if received > net:
                    errors.append(
                        f"Line {line}: amount_received cannot exceed net_amount."
                    )
            except (InvalidOperation, TypeError, KeyError):
                pass

            if row.get("status", "").upper() == "VERIFIED":
                if not (row.get("proof_url") or "").strip():
                    errors.append(
                        f"Line {line}: VERIFIED records require a proof reference."
                    )

            records.append(row)

    return errors, records


def main():
    errors, records = check_ledger()

    REPORTS.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    report = REPORTS / "latest-report.md"

    verified_received = Decimal("0")
    verified_net = Decimal("0")

    for row in records:
        if (row.get("status") or "").upper() == "VERIFIED":
            try:
                verified_received += Decimal(row["amount_received"])
                verified_net += Decimal(row["net_amount"])
            except (InvalidOperation, KeyError):
                pass

    lines = [
        "# APIP Automated Validation Report",
        "",
        f"- Generated UTC: {now.isoformat()}",
        f"- Ledger records: {len(records)}",
        f"- Validation: {'PASS' if not errors else 'FAIL'}",
        "- AI API enabled: NO",
        "- External outreach performed: NO",
        "- Money movement performed: NO",
        "",
        "## Financial evidence",
        "",
        f"- Verified net amount recorded: {verified_net}",
        f"- Verified amount received recorded: {verified_received}",
        "",
        "These figures reflect ledger entries only; they are not independently "
        "verified bank balances. A proof reference is not itself proof that a "
        "transaction is genuine.",
        "",
        "## Validation findings",
        "",
    ]

    if errors:
        lines.extend(f"- ERROR: {error}" for error in errors)
    else:
        lines.append("- No ledger schema or arithmetic errors detected.")

    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("APIP local validation")
    print(f"Ledger records: {len(records)}")
    print(f"Errors: {len(errors)}")
    print(f"Report: {report.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
