# AI Personal Income Protocol (APIP)

A reusable, evidence-driven system for testing whether AI-assisted work can produce real income, starting with zero operating cost.

## Principles
- Zero paid API or operating costs until verified earnings and explicit owner approval.
- Distinguish proposed income from customer payments and actual payouts.
- Keep project handovers, decisions, state, and tasks in version control.
- Validate changes with automated tests before publishing.
- Never store banking credentials, passwords, PINs, OTPs, or API keys in this repository.

## Run locally
Requires Python 3.13 or compatible Python 3.

Run automated tests:

    python -m unittest discover -s tests -v

Validate the income ledger and generate a report:

    python scripts/run_protocol.py

Report output:

    reports/latest-report.md

## Automation
The GitHub Actions workflow is configured to support scheduled and manual validation. Its first successful run remains to be verified.

## Financial truth
A passing test means the software passed its checks. It does not mean income has been earned. Ledger figures are only as reliable as their evidence.

## Handover
Before handing work to another builder, read HANDOVER.md, PROJECT_STATE.md, DECISIONS.md, and TASKS.md.
