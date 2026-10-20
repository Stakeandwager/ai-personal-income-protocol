# APIP bounded execution workflow — foundation

## Product contract

APIP takes a plain-language objective, turns proposed steps into typed actions, checks each action against owner authority and available capabilities, executes permitted work, and records evidence. The objective is a goal; it is not blanket permission to contact people, spend, sign, publish, or move money.

## Implemented in this milestone

- `scripts/apip_workflow.py` assigns action policy itself; a model cannot mark its own step safe or approved.
- `prepare_proposal_draft` is an allowlisted local action. It writes a reviewable Markdown draft and an append-only event with a SHA-256 evidence hash. Missing profile facts remain explicit placeholders.
- Public listing research and marketplace submission are marked `CAPABILITY_MISSING`; APIP does not ask the owner to approve an action it cannot perform.
- Spending is blocked until the opening balance is verified and the specific amount is within an explicit owner limit. An unknown ledger is not treated as zero.
- Contract acceptance and money movement are `OWNER_HANDOFF` actions.
- Unsupported action types fail closed. No action reports payment as verified.

## Current limits

This policy kernel is an engineering foundation, not yet wired into the private console's AI plan display. The console still produces free-text plans. No marketplace, web-research, communication, spending, contract, or payment adapter is registered here. Consequently, this release can execute local draft preparation only; it cannot submit the first commercial application.

The next integration should make the planner return a typed action list, persist the policy envelope with the plan, add a permitted public-source research adapter, and surface a scoped approval only when a verified external-action adapter is available. Preserve evidence from source retrieval, owner approval, submission receipt, contract, delivery, and payment as separate events.

## Verification

Run `python -m unittest discover -s tests -p test_apip_workflow.py -v`. The suite checks that generated objectives do not authorize outreach, local drafts preserve unverified facts as placeholders, spend and legal actions fail closed, and only allowlisted local work can execute.
