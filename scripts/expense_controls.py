"""Local, fail-closed USD expense accounting controls; no payment integration or FX conversion."""
from __future__ import annotations

import sqlite3
import os
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

AUTHORIZED_LIMIT_MINOR = 100_000  # USD 1,000.00, stored as cents
LEDGER_VERSION = "2"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_PATH = ROOT / "data" / "private-spending" / "expenses.sqlite3"


class ExpenseError(RuntimeError):
    pass


class LedgerUnavailable(ExpenseError):
    pass


class BudgetExceeded(ExpenseError):
    pass


class DuplicateTransaction(ExpenseError):
    pass


def _minor_units(amount: Decimal | str | int) -> int:
    if isinstance(amount, float):
        raise ExpenseError("Floating-point amounts are not accepted; use Decimal, string, or integer USD.")
    try:
        value = Decimal(str(amount))
        if not value.is_finite() or value <= 0:
            raise ExpenseError("Amount must be a positive USD amount.")
        rounded = value.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ExpenseError("Amount must be a valid positive USD amount.") from None
    if rounded != value:
        raise ExpenseError("Amount must be positive and have at most two decimal places.")
    return int(value * 100)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExpenseLedger:
    """SQLite-backed ledger. Missing/corrupt ledgers never silently reset."""

    def __init__(self, path: Path):
        self.path = Path(path)
        if not self.path.exists() or self.path.stat().st_size == 0:
            raise LedgerUnavailable("Expense ledger is missing or empty; explicit opening-balance initialization is required.")
        try:
            with closing(self._connect()) as db:
                self.limit_minor = self._validate_db(db)
        except (sqlite3.DatabaseError, KeyError, ValueError) as exc:
            raise LedgerUnavailable(f"Cannot read expense ledger safely ({exc}); spending blocked.") from None

    @classmethod
    def open_default(cls) -> "ExpenseLedger":
        """Open the local ledger without creating or resetting it."""
        return cls(DEFAULT_LEDGER_PATH)

    @staticmethod
    def initialize(path: Path, *, opening_spend_usd: Decimal | str | int, opening_evidence: str,
                   authorized_limit_usd: Decimal | str | int = Decimal("1000.00")) -> "ExpenseLedger":
        """Create a new USD-only ledger with an evidenced cumulative opening balance. Non-USD conversion is deliberately unsupported."""
        path = Path(path)
        if path.exists():
            raise LedgerUnavailable("Ledger path already exists; it will not be overwritten.")
        limit_minor = _minor_units(authorized_limit_ngn)
        opening_minor = _minor_units(opening_spend_ngn) if Decimal(str(opening_spend_ngn)) != 0 else 0
        if limit_minor > AUTHORIZED_LIMIT_MINOR:
            raise ExpenseError("Configured limit exceeds the owner's USD 1,000 lifetime authorization.")
        evidence = (opening_evidence or "").strip()
        if not evidence:
            raise ExpenseError("A source reference for the cumulative opening balance is required.")
        if opening_minor > limit_minor:
            raise BudgetExceeded("Opening cumulative spend already exceeds the authorized limit.")
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # O_EXCL prevents two initializers from silently replacing each other.
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
            os.close(fd)
            with closing(sqlite3.connect(path)) as db:
                db.execute("PRAGMA synchronous=FULL")
                db.executescript("""
                    CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                    CREATE TABLE expenses (
                        expense_id TEXT PRIMARY KEY,
                        amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),
                        status TEXT NOT NULL CHECK(status IN ('PROPOSED','ATTEMPTED','COMPLETED','VERIFIED','FAILED','CANCELLED')),
                        transaction_ref TEXT UNIQUE,
                        receipt_ref TEXT,
                        authorization_ref TEXT,
                        created_at_utc TEXT NOT NULL,
                        updated_at_utc TEXT NOT NULL
                    );
                    CREATE TABLE expense_events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        expense_id TEXT NOT NULL REFERENCES expenses(expense_id),
                        event TEXT NOT NULL,
                        evidence_ref TEXT NOT NULL,
                        at_utc TEXT NOT NULL
                    );
                """)
                db.executemany("INSERT INTO metadata(key,value) VALUES(?,?)", (
                    ("version", LEDGER_VERSION),
                    ("authorized_limit_minor", str(limit_minor)),
                    ("opening_spend_minor", str(opening_minor)),
                    ("opening_evidence", evidence),
                ))
                db.commit()
            return ExpenseLedger(path)
        except Exception:
            # Leave any partially written file in place; subsequent opens fail closed.
            raise

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA busy_timeout=10000")
            return db
        except Exception:
            db.close()
            raise

    def _validate_db(self, db: sqlite3.Connection, expected_limit: int | None = None) -> int:
        try:
            metadata = dict(db.execute("SELECT key, value FROM metadata"))
            if metadata.get("version") != LEDGER_VERSION or not metadata.get("opening_evidence"):
                raise LedgerUnavailable("Unsupported or incomplete ledger metadata; spending blocked.")
            limit = int(metadata["authorized_limit_minor"])
            opening = int(metadata["opening_spend_minor"])
            if limit <= 0 or limit > AUTHORIZED_LIMIT_MINOR or opening < 0 or opening > limit:
                raise LedgerUnavailable("Ledger authorization or opening balance is inconsistent; spending blocked.")
            if expected_limit is not None and limit != expected_limit:
                raise LedgerUnavailable("Ledger authorization changed while open; spending blocked.")
            check = db.execute("PRAGMA quick_check").fetchone()
            if not check or check[0] != "ok":
                raise LedgerUnavailable("Ledger integrity check failed; spending blocked.")
            allocation = int(db.execute(
                "SELECT COALESCE(SUM(amount_minor),0) FROM expenses WHERE status IN ('ATTEMPTED','COMPLETED','VERIFIED')"
            ).fetchone()[0])
            invalid = db.execute("""
                SELECT 1 FROM expenses WHERE
                    amount_minor <= 0 OR
                    (status IN ('ATTEMPTED','COMPLETED','VERIFIED') AND (transaction_ref IS NULL OR authorization_ref IS NULL)) OR
                    (status='VERIFIED' AND (receipt_ref IS NULL OR receipt_ref=''))
                LIMIT 1
            """).fetchone()
            if opening + allocation > limit or invalid:
                raise LedgerUnavailable("Ledger contains inconsistent totals or evidence; spending blocked.")
            return limit
        except LedgerUnavailable:
            raise
        except (sqlite3.DatabaseError, KeyError, TypeError, ValueError) as exc:
            raise LedgerUnavailable(f"Ledger validation failed; spending blocked ({exc}).") from None

    def _record_event(self, db: sqlite3.Connection, expense_id: str, event: str, evidence_ref: str) -> None:
        db.execute("INSERT INTO expense_events(expense_id,event,evidence_ref,at_utc) VALUES(?,?,?,?)",
                   (expense_id, event, evidence_ref.strip(), _now()))

    def propose(self, expense_id: str, amount_usd: Decimal | str | int, *, description: str) -> None:
        amount = _minor_units(amount_ngn)
        if not expense_id.strip() or not description.strip():
            raise ExpenseError("Expense ID and description are required.")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                self._validate_db(db, self.limit_minor)
                now = _now()
                db.execute("INSERT INTO expenses(expense_id,amount_minor,status,created_at_utc,updated_at_utc) VALUES(?,?,'PROPOSED',?,?)",
                           (expense_id.strip(), amount, now, now))
                self._record_event(db, expense_id.strip(), "PROPOSED", description)
                db.commit()
            except sqlite3.IntegrityError as exc:
                db.rollback()
                if "expense_id" in str(exc):
                    raise ExpenseError("Duplicate expense ID.") from None
                raise ExpenseError(f"Expense proposal rejected ({exc}).") from None

    def begin_attempt(self, expense_id: str, *, transaction_ref: str, authorization_ref: str) -> None:
        if not transaction_ref.strip() or not authorization_ref.strip():
            raise ExpenseError("Transaction reference and owner authorization reference are required.")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                self._validate_db(db, self.limit_minor)
                row = db.execute("SELECT amount_minor,status FROM expenses WHERE expense_id=?", (expense_id,)).fetchone()
                if not row or row[1] != "PROPOSED":
                    raise ExpenseError("Only a proposed expense can be attempted.")
                opening = int(dict(db.execute("SELECT key,value FROM metadata"))["opening_spend_minor"])
                reserved = db.execute("SELECT COALESCE(SUM(amount_minor),0) FROM expenses WHERE status IN ('ATTEMPTED','COMPLETED','VERIFIED')").fetchone()[0]
                if opening + int(reserved) + int(row[0]) > self.limit_minor:
                    raise BudgetExceeded("Attempt would exceed the remaining cumulative USD authorization.")
                now = _now()
                db.execute("UPDATE expenses SET status='ATTEMPTED',transaction_ref=?,authorization_ref=?,updated_at_utc=? WHERE expense_id=?",
                           (transaction_ref.strip(), authorization_ref.strip(), now, expense_id))
                self._record_event(db, expense_id, "ATTEMPTED", authorization_ref)
                db.commit()
            except sqlite3.IntegrityError:
                db.rollback()
                raise DuplicateTransaction("Transaction reference is already recorded.") from None
            except Exception:
                db.rollback()
                raise

    def mark_completed(self, expense_id: str, *, receipt_ref: str | None = None) -> None:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            self._validate_db(db, self.limit_minor)
            row = db.execute("SELECT status,transaction_ref FROM expenses WHERE expense_id=?", (expense_id,)).fetchone()
            if not row or row[0] != "ATTEMPTED" or not row[1]:
                db.rollback()
                raise ExpenseError("Only an attempted transaction with evidence can be completed.")
            db.execute("UPDATE expenses SET status='COMPLETED',receipt_ref=?,updated_at_utc=? WHERE expense_id=?",
                       (receipt_ref.strip() if receipt_ref else None, _now(), expense_id))
            self._record_event(db, expense_id, "COMPLETED", receipt_ref or row[1])
            db.commit()

    def verify(self, expense_id: str, *, receipt_ref: str) -> None:
        if not receipt_ref.strip():
            raise ExpenseError("Receipt reference is required for verification.")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            self._validate_db(db, self.limit_minor)
            row = db.execute("SELECT status,transaction_ref FROM expenses WHERE expense_id=?", (expense_id,)).fetchone()
            if not row or row[0] != "COMPLETED" or not row[1]:
                db.rollback()
                raise ExpenseError("Only a completed, evidenced transaction can be verified.")
            db.execute("UPDATE expenses SET status='VERIFIED',receipt_ref=?,updated_at_utc=? WHERE expense_id=?",
                       (receipt_ref.strip(), _now(), expense_id))
            self._record_event(db, expense_id, "VERIFIED", receipt_ref)
            db.commit()

    def mark_failed(self, expense_id: str, *, failure_evidence: str) -> None:
        if not failure_evidence.strip():
            raise ExpenseError("Failure evidence is required before releasing a reserved attempt.")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            self._validate_db(db, self.limit_minor)
            row = db.execute("SELECT status FROM expenses WHERE expense_id=?", (expense_id,)).fetchone()
            if not row or row[0] != "ATTEMPTED":
                db.rollback()
                raise ExpenseError("Only an attempted transaction can be marked failed.")
            db.execute("UPDATE expenses SET status='FAILED',updated_at_utc=? WHERE expense_id=?", (_now(), expense_id))
            self._record_event(db, expense_id, "FAILED", failure_evidence)
            db.commit()

    def cancel_proposal(self, expense_id: str, *, reason: str) -> None:
        if not reason.strip():
            raise ExpenseError("Cancellation reason is required.")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            self._validate_db(db, self.limit_minor)
            row = db.execute("SELECT status FROM expenses WHERE expense_id=?", (expense_id,)).fetchone()
            if not row or row[0] != "PROPOSED":
                db.rollback()
                raise ExpenseError("Only a proposed expense can be cancelled.")
            db.execute("UPDATE expenses SET status='CANCELLED',updated_at_utc=? WHERE expense_id=?", (_now(), expense_id))
            self._record_event(db, expense_id, "CANCELLED", reason)
            db.commit()

    def summary(self) -> dict[str, int]:
        try:
            with closing(self._connect()) as db:
                self._validate_db(db, self.limit_minor)
                opening = int(dict(db.execute("SELECT key,value FROM metadata"))["opening_spend_minor"])
                reserved = db.execute("SELECT COALESCE(SUM(amount_minor),0) FROM expenses WHERE status='ATTEMPTED'").fetchone()[0]
                spent = db.execute("SELECT COALESCE(SUM(amount_minor),0) FROM expenses WHERE status IN ('COMPLETED','VERIFIED')").fetchone()[0]
                return {"authorized_limit_minor": self.limit_minor,
                        "opening_spend_minor": opening,
                        "spent_minor": opening + int(spent),
                        "reserved_minor": int(reserved),
                        "remaining_minor": self.limit_minor - opening - int(spent) - int(reserved)}
        except (sqlite3.DatabaseError, KeyError, ValueError) as exc:
            raise LedgerUnavailable(f"Expense ledger read failed; spending blocked ({exc}).") from None
