# Changelog

## 2026-10-20
- Hardened private-console POST parsing: reject invalid or missing lengths, oversized bodies, truncated bodies, and form submissions with more than 12 fields using client error responses.
- Added HTTP-level regression coverage confirming malformed requests are rejected and the server remains responsive.
- Updated project task priority and handover state to match verified repository behavior and test results.
- Regenerated `reports/latest-report.md` by running the ledger validator; it reports PASS with an empty ledger and no verified income.
- Updated the existing automation in place from daily to every two hours; its ACTIVE status and saved recurrence were confirmed. Added an exclusive project run lock and made the automation acquire/release that lease.
- Added SQLite-based, fail-closed NGN expense accounting controls with a hard cap, transaction uniqueness, evidence lifecycle, and missing/corrupt/inconsistent ledger handling.
- Regenerated `reports/latest-report.md`; the income ledger has zero records and validation passes.
- Audited available connectors: no connected purchasing, APIP publishing, email, or CRM account was available; no purchase, message, or publication was attempted.
- Searched current public Upwork buyer briefs and official payment/fee/Connects guidance; recorded five ranked opportunities, source limits, offer terms, estimates, costs, blockers, and success criteria in `reports/first-income-source-experiment-2026-10-20.md`.
- Added a fictional spreadsheet-cleanup before/after sample and APIP safe market-access/privacy rules. No client data or financial details were added; no proposal, message, purchase, publication, or payment occurred. Cash spend was NGN 0; cumulative historical spend remains unknown.
- Updated the existing two-hour APIP automation in place to perform recurring public opportunity discovery, including oil/agriculture-related services, preserve source evidence, and prepare campaigns without sending through unavailable accounts. The update returned ACTIVE; the first scheduled online discovery run remains unverified.
- Recorded the owner-requested NGN 10,000/day verified-net-receipts target as a measurement goal, not a promise or spend permission; clarified that APIP “mining” means permitted opportunity discovery, not cryptocurrency mining or asset trading.
