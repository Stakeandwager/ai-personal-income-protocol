# Project State

## Project
AI Personal Income Protocol (APIP)

## Verified environment
- Windows, Python 3.13.5, Git installed.
- Local repository: `C:\Users\Owner\Projects\ai-personal-income-protocol`.
- Branch `main` tracks `origin/main`; working tree contains substantial pre-existing user changes. Preserve them.

## Capability audit — 2026-10-20

| Capability | Status | Evidence / exact blocker |
|---|---|---|
| Recurring local engineering and public opportunity discovery | **CONFIGURED, EXECUTION UNVERIFIED** | Existing Codex automation `apip-autonomous-build` remains ACTIVE on its existing two-hour recurrence. Its prompt was updated in place to discover current public paid opportunities, capture source evidence, include oil/agriculture services, and maintain safe draft-only marketing unless connected-account/authorization gates are met. The scheduler update returned ACTIVE; no scheduled online discovery run has yet been observed. Local tasks depend on the Codex desktop runtime being available. See `docs/APIP_INCOME_RADAR.md`. |
| Expense accounting controls | **IMPLEMENTED, INTEGRATION BLOCKED** | `scripts/expense_controls.py` uses SQLite, an NGN 10,000.00 ceiling, unique transaction references, attempt-time hard stop, receipt evidence, lifecycle events, and fail-closed database checks. Ten isolated simulation tests pass. No live expense database was initialized because cumulative prior APIP spend is not evidenced. |
| Real purchasing | **BLOCKED — OWNER ACTION REQUIRED** | No purchasing or payment-authorizing connector is available in the active tool inventory. Stripe appeared in plugin search as available but uninstalled, and is a payment connector rather than proof of a purchasing account. No payment credentials or authorization were accessible. Connect a suitable purchasing method and establish an evidenced cumulative opening spend before a real attempt. No purchase was made; actual cumulative remaining balance is unknown (maximum authorization is NGN 10,000 total). |
| APIP publishing | **BLOCKED — OWNER ACTION REQUIRED** | No APIP-owned website/publication account is connected. WordPress.com and Metricool appeared in plugin search but are uninstalled. The GitHub connector returned only the public `Stakeandwager/genesis` repository, not this APIP repo; it is not a suitable APIP marketing channel. Identify and connect an APIP-owned channel. No content was published. |
| Business outreach and replies | **BLOCKED — OWNER ACTION REQUIRED** | No email or CRM tools/accounts are connected in this task. Gmail is DISABLED_BY_ADMIN; Outlook Email, Apollo, Close, and other mail/CRM options appeared in plugin search as uninstalled. Connect an authorized mailbox/CRM and define the relevant APIP offer/recipient basis; no message was sent and no contact data was retained. |

No suitable real purchase, marketplace account, publishing channel, or outreach recipient was available, so no external commercial action was attempted. The addendum's NGN 10,000 cumulative authorization is recorded in `DECISIONS.md`; prior spend and remaining budget are not established, and the test-only database balances do not count as real spend.

## First income-sourcing experiment — 2026-10-20

- Current discovery found five public Upwork buyer briefs. Strongest fit: spreadsheet/database cleanup, with a proposed US$10 fixed-price offer to clean up to 100 client-provided rows and return a cleaned CSV plus exceptions/QA notes within 24 hours. The source listing displayed 20–50 proposals, one hire, and a buyer profile with US$4.2K spend/269 hires/16 active. This signals a buyer request and platform activity; it does not establish APIP-specific demand or current listing availability.
- A synthetic sample is at `examples/spreadsheet-cleanup-demo-v1/`. Safe market-access rules are at `docs/APIP_SAFE_MARKET_ACCESS.md`. Full sources, ranks, estimates, costs, and plan are in `reports/first-income-source-experiment-2026-10-20.md`.
- Research used current web search and official Upwork Help pages. Upwork listing open calls returned HTTP 403, so listing status and details were not independently refreshed. No Upwork connector surfaced; candidate outreach/publishing apps and Stripe were `installed:false`. Connected GitHub access lists only `Stakeandwager/genesis`, not APIP.
- No Upwork account was connected, no proposal or message was sent, no purchase/publication/delivery occurred, and no payment was received. This run spent NGN 0. Actual cumulative prior APIP spend remains unknown, so the authorized NGN 10,000 total ceiling has no evidence-backed remaining amount and the live expense database remains uninitialized.
- Next action requires an authorized freelancer account: verify the selected listing is open, check Connects and fee, and submit the prepared bounded offer only if no new spending is needed or the opening ledger is established and permits it.
- Owner target recorded: NGN 10,000/day independently verified net receipts. This is not a guarantee, forecast, or spend allowance. “Mining” is defined in APIP as permitted opportunity discovery, not crypto-mining or asset trading.

## Project capabilities and limitations
- Existing local ledger validator, deterministic opportunity generator/cycle, loopback-only private console, offline-first planner, and local JSONL records remain available.
- No verified income recorded. No paid API call, actual purchase, publication, customer outreach, or money movement occurred in this session.
- The GitHub Actions workflow still grants `contents: write` and pushes generated reports; behavior and permissions remain unverified.

## Tests and next action
- Baseline: `python -m unittest discover -s tests -v` — 31 passed.
- After first console fix: same command — 34 passed.
- Current full suite: `python -m unittest discover -s tests -v` — 47 passed. Expense controls: 10 tests; run lock: 3 tests. Initial implementation failures and diagnoses are recorded in `TEST_RESULTS.md`.
- Next: observe the first scheduled two-hour automation run and verify lock acquisition/release, then implement explicit private-console outcome transitions. The Scheduled UI's next-run time remains to be checked.
- For the commercial experiment, next: establish a source-backed expense opening balance and connect an authorized Upwork account; confirm the selected listing remains open, then review Connects and submit if the no-spend/ledger gate allows.
- For recurring discovery, next: observe a scheduled run and independently verify that it searches public sources and records sourced opportunities rather than recycling generated hypotheses.
- Current run lock was released after tests; `python scripts/apip_run_lock.py status` confirmed no lock is held.
- See `TEST_RESULTS.md` for full commands, failures, and results.
