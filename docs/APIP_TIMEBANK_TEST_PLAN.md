# APIP TimeBank — Test Plan

## Automated local checks
Run from the repository root:

    python -m unittest discover -s tests -v

The new economic tests cover verified versus pending/restricted funds, approved deductions, proportional allocations, zero pools/points, duplicates, currency separation, deterministic rounding, and invalid negative inputs. Extension checks validate Manifest V3, minimal permissions, referenced files, and the absence of network API calls in the current extension scripts.

## Manual Chromium acceptance checklist
- [ ] Load browser-extension/timebank/ via chrome://extensions → Developer mode → Load unpacked.
- [ ] Confirm no broad host permissions are requested.
- [ ] Attempt to start without activity label; confirm it is blocked.
- [ ] Attempt to start without consent; confirm it is blocked.
- [ ] Start a session, close/reopen the popup, and confirm the active session remains visible.
- [ ] Stop a session and confirm the local history record is marked RECORDED_UNVERIFIED and eligibleForRewards is false.
- [ ] Export history and inspect CSV escaping and values.
- [ ] Delete history and confirm after reload that it is empty.
- [ ] Start a session, restart the browser, and confirm it is marked INTERRUPTED with unknown duration, excluded from rewards.
- [ ] Inspect extension service-worker and popup consoles for errors.

## Limits
Automated source checks are not a substitute for running the extension in Chromium. Until the manual checklist is executed and documented, browser installation is NOT VERIFIED. No real payment, subscription, or external data transfer is implemented.
