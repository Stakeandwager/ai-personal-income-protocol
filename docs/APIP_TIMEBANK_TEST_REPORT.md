# APIP TimeBank — Test Report

**Status:** Automated checks passed; real Chromium installation remains unverified.

## Successful GitHub Actions run
- Workflow: APIP TimeBank validation
- Run ID: 40209499723
- Run URL: https://github.com/Stakeandwager/ai-personal-income-protocol/actions/runs/40209499723
- Tested head commit: 89d8352304bd8d111ec8c6bcf08c69822f02151d
- Full repository regression suite: PASS — 77 tests passed.
- TimeBank-focused suite: PASS — 13 tests passed.
- Manifest JSON validation: PASS.
- Node.js syntax checks for popup.js and service-worker.js: PASS.
- Extension ZIP packaging: PASS.
- Artifact upload: PASS — artifact ID 12605013918, named APIP_TimeBank_Extension_v0.1.0.
- Downloaded package integrity: PASS. The inner ZIP passed unzip -t and contains manifest.json, popup.html, popup.css, popup.js, and service-worker.js.
- Local package SHA-256: ce8074f55675214043b69decc5c792f290628fc7024824a6c1cd19cb5281841f

## Fixes made during validation
- Corrected the proportional-allocation test example: a pool of 80,000 minor units and weights 100:200:500 correctly allocates 10,000, 20,000, and 50,000 minor units.
- Corrected the existing CSRF-form test fixture to include a non-terminal saved plan so the expected second form is rendered. No console production code was changed for this test fix.
- Re-ran the complete suite successfully after these changes.

## Not run / not verified
- Real Chromium installation and manual UI testing: NOT RUN.
- Browser restart and interruption behavior in a real browser: NOT RUN.
- Independent verification of funding evidence: NOT IMPLEMENTED; the engine trusts the caller-provided VERIFIED status and does not inspect bank/provider records.
- Real subscriptions, wallet, or payments: NOT IMPLEMENTED and intentionally disabled.
- Patent filing, legal ownership assignments, and regulatory classification: NOT VERIFIED.

## Interpretation
Passing automated checks verifies the tested source and calculation logic only. It does not establish that APIP is a live income service, that activity has commercial value, or that any subscriber is owed or has received money.
