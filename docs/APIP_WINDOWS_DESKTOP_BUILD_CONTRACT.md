# APIP Windows Desktop Application — Build Contract

**Status:** approved direction; implementation not yet complete  
**Branch:** `feat/apip-windows-desktop`  
**Goal:** a Windows desktop application that can be launched as an `.exe` and updated in small, testable increments.

## Product objective

APIP discovers real problems and commercial opportunities from permitted public sources, groups duplicates, ranks opportunities using explicit evidence, and helps turn the strongest opportunities into deliverable work and verified receipts. It must not treat an idea, a job budget, a generated report, or an unsubmitted offer as income.

## User experience

The owner should be able to:
- launch APIP from a desktop shortcut without typing commands;
- see saved opportunities, source URLs, dates, evidence, status, and next action;
- start and stop a discovery run and see errors instead of silent failure;
- review why each opportunity was ranked highly;
- preserve records between sessions;
- export records and reports;
- inspect leads, offers, delivery, expenses, and actual receipts separately;
- update the application without losing its local data.

## Architecture decision

1. **Keep Python as the first desktop runtime.** The repository already contains Python opportunity, workflow, CSV-cleanup, and financial-control code. Reuse suitable modules rather than rewriting the project.
2. **Use a local SQLite database** for durable opportunities and run history. Store the database in a user-writable application-data directory, not inside the installation folder.
3. **Build a simple desktop shell first.** Prefer a low-resource native interface and avoid requiring a browser tab or paid cloud service just to open APIP.
4. **Separate source adapters from ranking.** Each adapter records source, URL, observed date, allowed-use notes, extracted text, and retrieval status. Respect robots rules, terms, rate limits, and API requirements; no login bypass or private-data collection.
5. **Rank evidence, not optimism.** Distinguish observed buyer request, explicit budget, repeated demand, competition, solution fit, estimated delivery effort, and unknowns. Scores are prioritization aids, not sale probabilities.
6. **Keep consequential actions gated.** Discovery and local analysis may run automatically. External messages, account creation, paid API use, purchases, contracts, publication, and money movement require the applicable owner authorization. Spending remains blocked until the opening cumulative balance is reconciled.
7. **Package for Windows.** Use a reproducible build script (evaluate PyInstaller first), produce a portable executable or installer, and retain a source-based developer mode. Do not claim an executable exists until the build artifact is created and launch-tested.

## Incremental milestones

### M0 — Repository and environment audit
- Inspect existing scripts, tests, current UI, dependencies, and Windows assumptions.
- Identify reusable code and any conflicts before editing.
- Record verified facts separately from assumptions.

### M1 — Desktop shell and local persistence
- Create the app window, navigation, status panel, and SQLite-backed opportunity list.
- Add sample/demo data clearly labelled as synthetic.
- Verify restart persistence and export.

### M2 — Real discovery adapters
- Start with sources that explicitly permit automated retrieval or offer a public API/feed.
- Record provenance, timestamps, deduplicate, retry safely, and show adapter errors.
- Do not scrape broadly without source-specific permission review.

### M3 — Evidence-based ranking and action queue
- Score explicit demand and feasibility transparently.
- Show evidence and unknowns behind each score.
- Generate a local draft offer or work plan; do not auto-send it.

### M4 — Income and cost reconciliation
- Connect to the existing ledgers only after compatibility review.
- Separate opportunity value, quoted price, invoice, received payment, fees, and net receipt.
- Preserve fail-closed spending behavior.

### M5 — Windows packaging and release checks
- Build from a clean checkout using documented commands.
- Run unit tests and a packaged smoke test on Windows.
- Verify data survives application restart and upgrade.
- Publish the executable only after a real artifact and checksum exist; never label a test report as a release.

## Definition of done for the first usable release

- Opens by double-clicking on a supported Windows PC.
- Does not require the owner to install Python separately if using the packaged build.
- Shows the same saved opportunities after closing and reopening.
- Can import/export opportunity data.
- Runs at least one permitted real discovery source and preserves source links and timestamps.
- Makes errors visible and does not invent results when a source fails.
- All tests pass and the packaged application is launched successfully on Windows.
- README states exactly what is implemented, what is not, and how to update it.

## Current honest status

This document establishes the product direction only. The Windows app, real multi-source crawler, installer, and verified executable are **not yet complete**. Existing `scripts/opportunity_engine.py` currently generates five hard-coded, unvalidated opportunity hypotheses; it is not yet a crawler. The next engineering increment is the M1 desktop shell and persistence, followed by a permitted source adapter.
