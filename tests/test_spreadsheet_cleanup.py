import csv
import tempfile
import unittest
from pathlib import Path

from scripts.spreadsheet_cleanup import CleanupError, clean_rows, process_file


class SpreadsheetCleanupTests(unittest.TestCase):
    def test_client_key_removes_duplicate_and_quarantines_conflict(self):
        headers = ["company", "email", "phone"]
        rows = [
            [" NORTHSTAR ", "JAMIE@EXAMPLE.INVALID ", "111"],
            ["Northstar", "jamie@example.invalid", "222"],
            [" Blue River ", "a@example.invalid", "333"],
            ["Blue River", "a@example.invalid", "333"],
        ]
        _, kept, exceptions = clean_rows(headers, rows, ["company", "email"])
        self.assertEqual(kept, [["Blue River", "a@example.invalid", "333"]])
        self.assertEqual([row[0] for row in exceptions], ["2", "3", "5"])
        self.assertTrue(exceptions[0][1].startswith("conflicting_key_values:"))
        self.assertEqual(exceptions[1][1], "conflicting_key_values:company,email,phone")
        self.assertEqual(exceptions[2][1], "duplicate_exact_after_trim")

    def test_missing_key_and_blank_rows_are_exceptions(self):
        _, kept, exceptions = clean_rows(
            ["email", "note"], [["", "unknown"], [" ", " "]], ["email"]
        )
        self.assertEqual(kept, [])
        self.assertEqual([row[1] for row in exceptions], ["missing_key_value:email", "empty_row"])

    def test_without_keys_only_trims_and_deduplicates_exact_rows(self):
        _, kept, exceptions = clean_rows(
            ["name", "note"], [[" Alice ", "One"], ["Alice", "One"], ["alice", "One"]]
        )
        self.assertEqual(kept, [["Alice", "One"], ["alice", "One"]])
        self.assertEqual(exceptions[0][1], "duplicate_exact_row")

    def test_invalid_headers_keys_and_ragged_rows_fail_closed(self):
        with self.assertRaises(CleanupError):
            clean_rows(["Name", " name "], [])
        with self.assertRaises(CleanupError):
            clean_rows(["name"], [["x"]], ["email"])
        with self.assertRaises(CleanupError):
            clean_rows(["name"], [["x", "extra"]])

    def test_opt_in_email_phone_formatting_is_conservative_and_quarantines_bad_values(self):
        _, kept, exceptions = clean_rows(
            ["email", "phone", "note"],
            [
                [" JAMIE@Example.COM ", "+1 (415) 555-0100", "valid"],
                ["not an email", "415-555-0101", "bad email"],
                ["sam@example.com", "555-ABCD", "bad phone"],
            ],
            email_columns=["EMAIL"],
            phone_columns=["phone"],
        )
        self.assertEqual(kept, [["JAMIE@example.com", "+14155550100", "valid"]])
        self.assertEqual([row[1] for row in exceptions], [
            "invalid_email_format:email",
            "invalid_phone_format:phone",
        ])
        self.assertEqual(exceptions[0][2:4], ["not an email", "415-555-0101"])
        self.assertEqual(exceptions[1][2:4], ["sam@example.com", "555-ABCD"])

    def test_format_columns_must_exist_and_cannot_overlap(self):
        with self.assertRaisesRegex(CleanupError, "Unknown Email column"):
            clean_rows(["phone"], [["+14155550100"]], email_columns=["email"])
        with self.assertRaisesRegex(CleanupError, "both email and phone"):
            clean_rows(["contact"], [["sample@example.invalid"]], email_columns=["contact"], phone_columns=["contact"])

    def test_mapping_guide_includes_proposals_and_unmapped_target_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "contacts.csv"
            source.write_text(
                "name,email,phone\nJamie Sample,JAMIE@EXAMPLE.INVALID,+1 (415) 555-0100\n",
                encoding="utf-8",
            )
            output = root / "output"
            process_file(
                source,
                output,
                email_columns=["email"],
                phone_columns=["phone"],
                target_fields=["Contact_Name", "Email", "Phone", "Account_Name"],
                field_map=["name=Contact_Name", "email=Email", "phone=Phone"],
            )
            guide_path = output / "mapping-guide-contacts.csv"
            with guide_path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["target_field"], "Contact_Name")
        self.assertEqual(rows[0]["mapping_status"], "proposed mapping; buyer confirmation required")
        self.assertIn("lowercase domain only", rows[1]["handling"])
        self.assertIn("no country-code inference", rows[2]["handling"])
        self.assertEqual(rows[-1]["source_column"], "")
        self.assertEqual(rows[-1]["target_field"], "Account_Name")
        self.assertEqual(rows[-1]["mapping_status"], "missing source; buyer decision required")

    def test_mapping_guide_rejects_unknown_or_duplicate_target_mappings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "contacts.csv"
            source.write_text("name,email\nJamie,j@example.invalid\n", encoding="utf-8")
            with self.assertRaisesRegex(CleanupError, "Unknown field-map source"):
                process_file(source, root / "unknown", field_map=["phone=Phone"])
            with self.assertRaisesRegex(CleanupError, "Target field mapped more than once"):
                process_file(source, root / "duplicate", field_map=["name=Contact", "email=Contact"])

    def test_file_processing_preserves_input_and_writes_quoted_utf8_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            original = "name,note\nZoë,\"hello, world\"\nZoë,\"hello, world\"\n".encode("utf-8")
            source.write_bytes(original)
            cleaned, exceptions, stats = process_file(source, root / "output")
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(stats, {
                "input_records": 2,
                "cleaned_records": 1,
                "exception_records": 1,
                "duplicates_removed": 1,
            })
            with cleaned.open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(list(csv.reader(stream)), [["name", "note"], ["Zoë", "hello, world"]])
            with exceptions.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(rows[0][:2], ["_apip_source_record", "_apip_issue"])
            self.assertEqual(rows[1][1], "duplicate_exact_row")

    def test_outputs_are_not_overwritten_without_force(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            source.write_text("name\nAlice\n", encoding="utf-8")
            output_dir = root / "output"
            process_file(source, output_dir)
            with self.assertRaisesRegex(CleanupError, "already exists"):
                process_file(source, output_dir)
            process_file(source, output_dir, force=True)

    def test_record_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            source.write_text("name\nAlice\nBob\n", encoding="utf-8")
            with self.assertRaisesRegex(CleanupError, "record limit"):
                process_file(source, root / "output", max_records=1)


if __name__ == "__main__":
    unittest.main()
