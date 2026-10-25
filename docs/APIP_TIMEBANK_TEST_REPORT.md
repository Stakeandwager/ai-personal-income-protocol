# APIP TimeBank — Test Report

**Report status:** Interim; browser installation is not verified.

## Verified GitHub Actions run
- Workflow: APIP TimeBank validation
- Run ID: 40209375566
- Run URL: https://github.com/Stakeandwager/ai-personal-income-protocol/actions/runs/40209375566
- Head commit at time of run: e5a39d1b51a9cd55271830db1e70f3763df3ba6a
- TimeBank-focused automated tests: PASS — 13 tests passed.
- Manifest JSON validation: PASS.
- Node.js syntax checks for popup.js and service-worker.js: PASS.
- Extension ZIP packaging: PASS.
- Artifact upload: completed; artifact ID 12604813976.
- Downloaded artifact was inspected locally. The inner extension ZIP passed unzip -t and contains manifest.json, popup.html, popup.css, popup.js, and service-worker.js.

## Full repository regression suite
- Initial run executed 77 tests and found two failures: an incorrect proportional-allocation expected value in a new TimeBank test, and a pre-existing CSRF-form test whose fixture did not supply a saved plan.
- The reward example was corrected to match the formula: an 80,000-minor-unit pool and point weights 100:200:500 allocate 10,000, 20,000, and 50,000 minor units.
- The CSRF test fixture was corrected to supply a non-terminal saved plan, which is required for the second form to appear. This changes the test setup, not the console implementation.
- A full regression rerun after these corrections is pending. Do not treat the full suite as passed until a subsequent CI run confirms it.

## Not run / not verified
- Real Chromium installation and manual UI testing: NOT RUN.
- Browser restart and interruption behavior in a real browser: NOT RUN.
- Independent verification of funding evidence: NOT IMPLEMENTED.
- Real subscriptions, wallet, or payments: NOT IMPLEMENTED and intentionally disabled.
- Patent filing, legal ownership assignments, and regulatory classification: NOT VERIFIED.

## Artifact
The workflow artifact is named APIP_TimeBank_Extension_v0.1.0. The Actions artifact expires according to the configured retention period. A copy was downloaded and the inner extension ZIP integrity checked during this build session.
