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

## Netlify owner app — prototype
The `web/` and `netlify/functions/` folders contain a Netlify-ready private owner dashboard. It is designed to show a public-source jobs feed, save leads and evidence, track owner-reported progress, draft offers, and mark payout-provider setup without storing bank credentials. The scheduled Remotive feed runs up to four times daily after Netlify deployment. It obeys the source's attribution and freshness rules.

The site is **not deployed** and this is not a validated commercial product. Before deployment, connect this repository to Netlify, enable invite-only Identity, invite the owner, and test a deploy preview. Applications, external outreach, contract signing, payment processing, and receipt verification are not implemented. Read `docs/APIP_NETLIFY_OWNER_APP.md` for setup and boundaries.

## Financial truth
A passing test means the software passed its checks. It does not mean income has been earned. Ledger figures are only as reliable as their evidence.

## Handover
Before handing work to another builder, read HANDOVER.md, PROJECT_STATE.md, DECISIONS.md, and TASKS.md.
