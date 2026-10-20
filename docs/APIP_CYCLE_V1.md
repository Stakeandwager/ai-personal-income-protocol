# APIP Cycle v1 — persistent next-action selection

## What it does

- Generates zero-cost opportunity hypotheses.
- Selects one next experiment and writes `reports/apip-next-action.md`.
- Records each selection in `data/experiment-events.jsonl`.
- Remembers recorded outcomes and moves to other ideas after a terminal test result.
- Explicitly reports that no AI model, outreach, spend, payment, or profit verification occurred.

## Run from repository root

```cmd
python scripts\opportunity_engine.py
python scripts\apip_cycle.py
python -m unittest discover -s tests -v
```

## Record outcomes

Edit `data/experiment-events.jsonl` only after a test actually happened. Add a separate JSON line with `opportunity_id`, a terminal `status` (`TESTED_NO_DEMAND`, `TESTED_DEMAND`, or `ABANDONED_WITH_REASON`), timestamp, evidence reference, and short notes. Never invent evidence. The next cycle uses the latest status for each opportunity. Do not overwrite the `SELECTED` event; append a new line.

## Scope and limits

This is a deterministic persistent cycle, not an AI reasoning runtime. It does not browse the internet, build the sample automatically, contact customers, publish offers, process payments, or transfer profit. Keep the cost ceiling at NGN 0 unless the owner explicitly approves a specific expense and action. The code cannot create credit or pay an obligation by recording a deficit.
