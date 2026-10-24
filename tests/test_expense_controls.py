import concurrent.futures
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from scripts.expense_controls import (
    BudgetExceeded,
    DuplicateTransaction,
    ExpenseError,
    ExpenseLedger,
    LedgerUnavailable,
)


class ExpenseControlTests(unittest.TestCase):
    """Tests use temporary databases and simulated evidence; no money moves."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "expenses.sqlite3"
        self.ledger = ExpenseLedger.initialize(
            self.path, opening_spend_usd="10.00", opening_evidence="SIMULATED OPENING BALANCE",
            authorized_limit_usd="100.00",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_owner_authorization_is_hard_capped_at_usd_1000(self):
        other = Path(self.temp.name) / "over-owner-cap.sqlite3"
        with self.assertRaises(ExpenseError):
            ExpenseLedger.initialize(other, opening_spend_usd="0", opening_evidence="SIM",
                                     authorized_limit_usd="1000.01")
        self.assertFalse(other.exists())

    def test_missing_ledger_fails_closed_until_opening_balance_is_evidenced(self):
        path = Path(self.temp.name) / "missing.sqlite3"
        with self.assertRaises(LedgerUnavailable):
            ExpenseLedger(path)
        self.assertFalse(path.exists())

    def test_budget_and_simulated_transaction_lifecycle(self):
        self.ledger.propose("demo-1", "90.00", description="Simulated one-off expense")
        self.ledger.begin_attempt("demo-1", transaction_ref="SIM-TXN-1", authorization_ref="SIM-OWNER-APPROVAL")
        self.assertEqual(self.ledger.summary()["remaining_minor"], 0)
        self.ledger.propose("demo-2", "0.01", description="Should be blocked at attempt")
        with self.assertRaises(BudgetExceeded):
            self.ledger.begin_attempt("demo-2", transaction_ref="SIM-TXN-2", authorization_ref="SIM-OWNER-APPROVAL")
        self.ledger.mark_completed("demo-1", receipt_ref="SIM-RECEIPT-1")
        self.assertEqual(self.ledger.summary()["spent_minor"], 10000)
        self.ledger.verify("demo-1", receipt_ref="SIM-RECEIPT-1")
        self.assertEqual(self.ledger.summary()["remaining_minor"], 0)

    def test_proposals_do_not_count_as_spending_until_attempted(self):
        self.ledger.propose("demo-1", "100.00", description="Simulated proposal")
        self.assertEqual(self.ledger.summary()["remaining_minor"], 9000)
        self.ledger.cancel_proposal("demo-1", reason="Simulation cancelled")
        self.assertEqual(self.ledger.summary()["remaining_minor"], 9000)

    def test_duplicate_expense_and_transaction_ids_are_rejected(self):
        self.ledger.propose("demo-1", "10.00", description="First simulated expense")
        self.ledger.propose("demo-2", "10.00", description="Second simulated expense")
        with self.assertRaises(ExpenseError):
            self.ledger.propose("demo-1", "1.00", description="Duplicate ID")
        self.ledger.begin_attempt("demo-1", transaction_ref="SIM-TXN", authorization_ref="SIM-AUTH")
        with self.assertRaises(DuplicateTransaction):
            self.ledger.begin_attempt("demo-2", transaction_ref="SIM-TXN", authorization_ref="SIM-AUTH")

    def test_verified_expense_requires_completed_transaction_and_receipt(self):
        self.ledger.propose("demo-1", "10.00", description="Simulated expense")
        with self.assertRaises(ExpenseError):
            self.ledger.verify("demo-1", receipt_ref="SIM-RECEIPT")
        self.ledger.begin_attempt("demo-1", transaction_ref="SIM-TXN", authorization_ref="SIM-AUTH")
        self.ledger.mark_completed("demo-1")
        with self.assertRaises(ExpenseError):
            self.ledger.verify("demo-1", receipt_ref="")
        self.ledger.verify("demo-1", receipt_ref="SIM-RECEIPT")
        with closing(sqlite3.connect(self.path)) as db:
            event_names = [row[0] for row in db.execute("SELECT event FROM expense_events ORDER BY event_id")]
        self.assertEqual(event_names, ["PROPOSED", "ATTEMPTED", "COMPLETED", "VERIFIED"])

    def test_failed_attempt_requires_evidence_and_releases_reservation(self):
        self.ledger.propose("demo-1", "90.00", description="Simulated attempt")
        self.ledger.begin_attempt("demo-1", transaction_ref="SIM-TXN", authorization_ref="SIM-AUTH")
        with self.assertRaises(ExpenseError):
            self.ledger.mark_failed("demo-1", failure_evidence="")
        self.ledger.mark_failed("demo-1", failure_evidence="SIM-DECLINED")
        self.assertEqual(self.ledger.summary()["remaining_minor"], 9000)

    def test_corrupt_and_zero_byte_ledgers_fail_closed(self):
        path = Path(self.temp.name) / "corrupt.sqlite3"
        path.write_bytes(b"not a sqlite database")
        with self.assertRaises(LedgerUnavailable):
            ExpenseLedger(path)
        empty = Path(self.temp.name) / "empty.sqlite3"
        empty.touch()
        with self.assertRaises(LedgerUnavailable):
            ExpenseLedger(empty)

    def test_inconsistent_stored_total_fails_closed(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE metadata SET value='10001' WHERE key='opening_spend_minor'")
            db.commit()
        with self.assertRaises(LedgerUnavailable):
            ExpenseLedger(self.path)

    def test_overlapping_attempts_cannot_exceed_budget(self):
        self.ledger.propose("demo-1", "60.00", description="Concurrent simulation A")
        self.ledger.propose("demo-2", "60.00", description="Concurrent simulation B")

        def attempt(expense_id, transaction_ref):
            try:
                self.ledger.begin_attempt(expense_id, transaction_ref=transaction_ref, authorization_ref="SIM-AUTH")
                return "accepted"
            except BudgetExceeded:
                return "blocked"

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda pair: attempt(*pair), (("demo-1", "SIM-A"), ("demo-2", "SIM-B"))))
        self.assertCountEqual(results, ["accepted", "blocked"])
        self.assertEqual(self.ledger.summary()["remaining_minor"], 3000)

    def test_initialization_never_overwrites_existing_file_or_exceeds_cap(self):
        with self.assertRaises(LedgerUnavailable):
            ExpenseLedger.initialize(self.path, opening_spend_usd="0", opening_evidence="SIM")
        other = Path(self.temp.name) / "over-cap.sqlite3"
        with self.assertRaises(ExpenseError):
            ExpenseLedger.initialize(other, opening_spend_usd="0", opening_evidence="SIM",
                                      authorized_limit_usd="1000.01")
        self.assertFalse(other.exists())


if __name__ == "__main__":
    unittest.main()
