# Reusable AI Builder Handover

## Mission
Build APIP into a reliable, evidence-driven system for assessing income opportunities, organizing explicitly authorized work, tracking delivery, and distinguishing proposed earnings from independently verified payments.

## Operating boundaries
- Keep paid AI services disabled unless the owner explicitly approves them.
- The owner authorized up to NGN 10,000 cumulative for a necessary one-off experiment, plus one relevant APIP marketing/customer-discovery experiment if suitable connected accounts exist. See DECISIONS.md. Do not use subscriptions/debt, exceed the cap, or act when payment/account permissions or prior cumulative spend are unverified.
- Do not commit or push. Respect account permissions, opt-outs, complaints, and the minimum-retention rule for contact information.
- Preserve existing user changes and private records. Never expose credentials or private financial data.
- Treat model output as advisory. Do not execute generated code or claim unverified income.

## Repository and records
- Repository: `C:\\Users\\Owner\\Projects\\ai-personal-income-protocol`
- Read `PROJECT_STATE.md`, `TASKS.md`, and `DECISIONS.md` at session start.
- Record actual test commands/results in `TEST_RESULTS.md`; meaningful changes in `CHANGELOG.md`.

## Current verified state — 2026-10-20
- Existing Codex automation `apip-autonomous-build` is ACTIVE every two hours, with a project-local exclusive lock. Configuration is verified; scheduled execution and next-run time are not yet verified.
- Local expense controls are implemented and simulation-tested, but there is no live ledger because prior cumulative spend is unknown. Real purchasing is integration-blocked.
- Publishing/outreach are blocked: there is no connected APIP channel, mailbox, or CRM. No external action was taken.
- First income-sourcing research found five current Upwork buyer briefs. The strongest-fit spreadsheet-cleanup offer and fictional sample are in `reports/first-income-source-experiment-2026-10-20.md` and `examples/spreadsheet-cleanup-demo-v1/`. No Upwork account is connected; listings could not be independently reopened due HTTP 403. No proposal, message, purchase, or payment occurred.
- `docs/APIP_SAFE_MARKET_ACCESS.md` defines public-research, connector, data-minimization, opt-out, and no-secrets boundaries for future marketing capability. Do not log or reuse the banking details pasted in chat.
- The existing two-hour `apip-autonomous-build` automation was updated in place to search current public work opportunities, including agriculture/oil-sector services, and record evidence. Its new prompt returned ACTIVE, but an actual scheduled discovery run remains unverified. See `docs/APIP_INCOME_RADAR.md`.
- Owner target is NGN 10,000/day verified net receipts, recorded as a target rather than a promise or daily spend limit. The project's cumulative experimental spend cap remains NGN 10,000 total with opening balance unknown. No cryptocurrency miner/trading is authorized.
- Baseline suite: 31 passed; prior console hardening suite: 34 passed; current expense and lock tests: 10 and 3 passed. See TEST_RESULTS.md, including initial failed runs and diagnoses.
- `python scripts/run_protocol.py`: previously PASS with an empty income ledger; no recorded income.
- Existing working tree contains substantial user additions and edits. Do not reset, overwrite unrelated files, or treat them as authored by this session.
- No commit, push, GitHub workflow run, paid API call, external outreach, or financial action was performed.

## Resume here
Start by checking for and acquiring the APIP project run lock (`python scripts/apip_run_lock.py acquire`). Do not clear an existing lock until no previous run is active. Then run the complete test suite and record the result. Continue with the first unchecked Priority 1 task in `TASKS.md`; update the durable project records with observed evidence. First verify one scheduled online opportunity-discovery run. To advance the commercial experiment, establish source-backed cumulative opening spend, connect an authorized marketplace account, and verify listing/Connects cost before any application that may require spend. For direct marketing, connect an APIP-owned channel/mailbox and use a relevant recipient basis under `docs/APIP_SAFE_MARKET_ACCESS.md`.
