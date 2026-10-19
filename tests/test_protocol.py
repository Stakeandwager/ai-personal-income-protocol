
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import run_protocol

FIELDS = run_protocol.FIELDS


def make_row(**overrides):
    row = {
        "record_id": "TEST-001",
        "date_utc": "2026-10-19",
        "experiment_id": "EXP-001",
        "event_type": "PAYMENT",
        "status": "VERIFIED",
        "currency": "NGN",
        "gross_amount": "100",
        "fees": "5",
        "refunds": "0",
        "other_costs": "10",
        "net_amount": "85",
        "amount_received": "85",
        "proof_url": "test-evidence-reference",
        "notes": "Automated test fixture only",
    }
    row.update(overrides)
    return row


class ProtocolLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temp.name) / "income-ledger.csv"

    def tearDown(self):
        self.temp.cleanup()

    def write_ledger(self, rows):
        with self.ledger.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        with patch.object(run_protocol, "LEDGER", self.ledger):
            return run_protocol.check_ledger()

    def test_empty_ledger_is_valid(self):
        self.write_ledger([])
        errors, records = self.validate()
        self.assertEqual(errors, [])
        self.assertEqual(records, [])

    def test_valid_record_passes(self):
        self.write_ledger([make_row()])
        errors, records = self.validate()
        self.assertEqual(errors, [])
        self.assertEqual(len(records), 1)

    def test_wrong_net_amount_is_rejected(self):
        self.write_ledger([make_row(net_amount="99")])
        errors, _ = self.validate()
        self.assertTrue(any("net_amount must equal" in e for e in errors))

    def test_duplicate_record_id_is_rejected(self):
        self.write_ledger([make_row(), make_row()])
        errors, _ = self.validate()
        self.assertTrue(any("duplicate record_id" in e for e in errors))

    def test_verified_record_needs_evidence_reference(self):
        self.write_ledger([make_row(proof_url="")])
        errors, _ = self.validate()
        self.assertTrue(any("require a proof reference" in e for e in errors))

    def test_negative_amount_is_rejected(self):
        self.write_ledger([make_row(fees="-5")])
        errors, _ = self.validate()
        self.assertTrue(any("fees must be a non-negative number" in e for e in errors))

    def test_received_amount_cannot_exceed_net(self):
        self.write_ledger([make_row(amount_received="90")])
        errors, _ = self.validate()
        self.assertTrue(any("cannot exceed net_amount" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
