# APIP Expense Controls

## Scope and status

`scripts/expense_controls.py` implements a local SQLite accounting control at `data/private-spending/expenses.sqlite3`. `ExpenseLedger.open_default()` opens it without creating or resetting it. It does not connect to a bank, card, store, or payment service and cannot prevent a purchase initiated separately in another application.

**Status: IMPLEMENTED, INTEGRATION BLOCKED.** Local lifecycle, cap, duplicate-reference, persistence, corruption, and concurrency behavior are tested with temporary simulated databases. No real expense ledger is initialized and no purchase was made.

## Authorized budget

- Cumulative ceiling: NGN 10,000.00.
- Prior cumulative APIP experiment spend is not established by the repository. Do not initialize the live ledger with zero by assumption.
- `ExpenseLedger.initialize` requires an explicit opening spend and supporting opening-evidence reference. Use a source-backed cumulative amount; if it cannot be established, do not enable real purchasing.
- The database is created under `data/private-spending/` and ignored by Git because receipt references may be private.

## Lifecycle and enforcement

1. `propose` records a proposed amount but does not count it as committed spend.
2. `begin_attempt` is the hard budget gate. It requires transaction and owner-authorization references, reserves budget, and serializes concurrent attempts using SQLite's immediate transaction lock.
3. `mark_completed` records a completed transaction and optional receipt reference.
4. `verify` records receipt evidence and marks the transaction verified.
5. `mark_failed` releases an attempted reservation only with failure evidence; ambiguous results must stay attempted and reserved.
6. A proposal may be cancelled with a reason.

Transaction references are unique. Verified status requires receipt evidence. Invalid, missing, empty, corrupt, unsupported, or inconsistent databases fail closed. Initialization never overwrites an existing file. Recovery requires preserving the damaged database, reconciling against source evidence, and creating a reviewed ledger with an evidenced opening balance; there is no automatic reset or repair.

These controls account for APIP-recorded expenses only. They are not a payment authorization system and do not restrict spending in other applications.

## Recurring-run lock

`python scripts/apip_run_lock.py acquire` creates an exclusive lease and prints its run ID. Keep the lease for the entire automation run and release it with `python scripts/apip_run_lock.py release <run-id>`. A pre-existing or corrupt lock blocks editing. Interrupted runs leave the lock in place; inspect active APIP tasks and recover manually rather than clearing it automatically. This fail-closed behavior can pause future runs until reviewed.
