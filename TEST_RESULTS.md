# Test Results

## 2026-10-20 — initial baseline
- Command: `python -m unittest discover -s tests -v`
- Result: PASS — 31 tests before the first console hardening change.

## 2026-10-20 — console request validation
- Command: `python -m unittest discover -s tests -v`
- Result: PASS — 34 tests.
- Added HTTP-level tests for non-numeric Content-Length (400 and server remains responsive), more than 12 form fields (400), and a truncated body (400).
- Initial run failed because the raw-socket test read only response headers; the test was corrected to read the full response.

## 2026-10-20 — expense ledger and scheduler lock implementation
- First full command: `python -m unittest discover -s tests -v`
- Result: FAIL — 46 tests, 9 setup errors. Diagnosis: SQLite metadata writes were not committed before reopening the new database; all cases failed closed as designed.
- First targeted retry: `python -m unittest discover -s tests -p 'test_expense_controls.py' -v`
- Result: FAIL — 9 tests, 2 cleanup errors on Windows. Diagnosis: a SQLite connection remained open on the corrupt-database error path, preventing temporary-file cleanup.
- After committing metadata and closing partially configured connections, final focused expense suite passed 10 tests, including cap, lifecycle/evidence, duplicate transaction, missing/corrupt/inconsistent ledger, and concurrent attempts.
- Focused lock suite: `python -m unittest discover -s tests -p 'test_apip_run_lock.py' -v` — PASS, 3 tests for concurrent acquisition, owner-only release, and corrupt-lock fail-closed behavior.
- Final regression suite: `python -m unittest discover -s tests -v` — PASS, 47 tests.

## 2026-10-20 — income ledger validation
- Command: `python scripts/run_protocol.py`
- Result: PASS — 0 income-ledger records, 0 validation errors. The ledger contains no recorded income.
- Report: `reports/latest-report.md`.

## 2026-10-20 — scheduler and connector audit
- Existing automation `apip-autonomous-build` was inspected at `C:\Users\Owner\.codex\automations\apip-autonomous-build\automation.toml`; prior rule was daily at 09:00.
- Updated that same automation (no duplicate created) to `FREQ=HOURLY;INTERVAL=2`. The scheduler update returned `status=ACTIVE`; the saved file confirms the rule, local execution environment, APIP project path, and exclusive-lock instructions.
- The scheduler API/config did not return an exact next-run timestamp or execution history. The Scheduled UI exposes next-run information. Local file tasks require the computer and desktop app to remain running, per [official OpenAI scheduled-task guidance](https://developers.openai.com/training/walkthroughs/scheduled-tasks). No scheduled execution has yet been observed.
- Connector discovery found no connected purchasing, APIP publishing, mail, or CRM accounts. GitHub repository listing returned `Stakeandwager/genesis`, not the APIP repository. No purchase, message, or publication was attempted.
- This session acquired the APIP exclusive run lock, ran the full 47-test suite, and released its own lock. A subsequent `status` check confirmed no lock was held.

## Scope of simulated finance tests
- Expense tests used temporary SQLite files and simulated references only. They did not create a live APIP expense ledger, access payment credentials, or make a purchase.
- Simulated balances do not count toward or establish the real cumulative NGN 10,000 budget balance.

## 2026-10-20 — pre-commit regression validation
- Command: `python -m unittest discover -s tests -v`
- Result: PASS — 47 tests.
- This run changed project records, examples, and the existing Codex automation prompt; no executable source changed after this validation.
