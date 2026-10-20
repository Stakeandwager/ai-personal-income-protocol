APIP OPPORTUNITY ENGINE + PERSISTENT CYCLE V1

1. Extract this ZIP. Merge its scripts, tests, docs, and .github folders into your existing APIP repo. Do not replace unrelated files.
2. From CMD, go to: C:\Users\Owner\Projects\ai-personal-income-protocol
3. Run:
   python scripts\opportunity_engine.py
   python scripts\apip_cycle.py
   python -m unittest discover -s tests -v
4. Review reports\apip-next-action.md and reports\apip-cycle-state.json.
5. If tests pass, commit the added files and workflow change using the instructions in docs\APIP_CYCLE_V1.md.

This build selects and records the next experiment. It is not yet an AI model and does not contact customers or claim income.
