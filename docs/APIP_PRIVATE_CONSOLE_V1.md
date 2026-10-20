# APIP Private Console v1

## What this milestone provides

- A private console bound only to `127.0.0.1` (your own computer).
- Offline demo planning with no API key and no API charge.
- Optional OpenAI Responses API integration when the owner explicitly enables it.
- Optional API web search, separately disabled by default.
- Live API plans use a typed JSON action list; the local policy kernel assigns statuses and retains URL citation annotations when web search is enabled.
- Local JSONL plan snapshots and audit records.
- A run button for the allowlisted local proposal-draft action, with a saved artifact and SHA-256 evidence reference.
- A manual outcome recorder that explicitly labels user-reported outcomes as unverified.
- Plan status is projected from the append-only outcome log: `DRAFT` or `IN_PROGRESS` may transition to one terminal result (`TESTED_DEMAND`, `TESTED_NO_DEMAND`, or `ABANDONED_WITH_REASON`). Terminal outcomes cannot be overwritten through the console.
- No execution of GPT-generated code, no customer outreach, no publishing, no purchases, no financial transfers, and no custody of funds.

## Windows quick start

1. Copy `scripts/private_console.py` and `run-apip-console.cmd` into the root of the APIP repository, keeping the `scripts` folder structure.
2. Add `data/private-console/` to `.gitignore` so private plans and notes remain local.
3. Double-click `run-apip-console.cmd`.
4. Open `http://127.0.0.1:8765` in your browser.
5. Press `Ctrl+C` in the terminal to stop the console.

Python 3.10+ is recommended. The console uses only the Python standard library.

## Optional live API mode

API access and billing are separate from a ChatGPT subscription. Do not enable paid API calls until you have reviewed billing and chosen a spending limit.

In the same Windows Command Prompt used to launch the console, set environment variables for that session:

```cmd
set OPENAI_API_KEY=YOUR_REAL_KEY_HERE
set OPENAI_MODEL=YOUR_AVAILABLE_API_MODEL
set APIP_ALLOW_PAID_API=1
set APIP_WEB_SEARCH=1
py -3 scripts\private_console.py
```

Replace placeholders in your terminal only; do not commit them, paste them into chat, or put them in browser code. If you do not explicitly approve API costs, leave `APIP_ALLOW_PAID_API=0`. With the default setting, the app does not make an API request and uses demo mode.

## Local private records

The app writes `data/private-console/plans.jsonl` and `data/private-console/events.jsonl`. These are intended to be ignored by Git. Do not put API keys, passwords, bank credentials, OTPs, medical records, or unnecessary personal/customer data in the console. Do not push private logs to a public repository.

## Trust boundary

GPT output is untrusted advice, not executable authority. Only typed local draft preparation has an executor. Public-source tasks and marketplace applications remain blocked without adapters. The prototype cannot log in to third-party sites, accept contracts, purchase anything, move money, or independently verify payment. The outcome recorder stores a user-reported status only. Evidence references should avoid exposing confidential details.

## Next build stages

1. Add a permitted source executor with source URL, capture time, eligibility evidence, and freshness checks.
2. Add verified marketplace integration; request scoped owner approval only immediately before a supported submission.
3. Add a background scheduler with hard runtime/API budgets and a kill switch.
4. Add OAuth integrations only for supported official APIs and the minimum necessary permissions.
5. Add payment-provider read-only reconciliation only if supported, consented to, and affordable.
6. Add local authentication before any remote hosting. Never expose this prototype's built-in server to the public internet.
