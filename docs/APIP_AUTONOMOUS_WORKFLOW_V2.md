# APIP bounded execution workflow — foundation

## Product contract

APIP takes a plain-language objective, turns proposed steps into typed actions, checks each action against owner authority and available capabilities, executes permitted work, and records evidence. The objective is a goal; it is not blanket permission to contact people, spend, sign, publish, or move money.

## Implemented in this milestone

- `scripts/apip_workflow.py` assigns action policy itself; a model cannot mark its own step safe or approved.
- The local console requests a typed JSON plan, stores the policy envelope as an append-only plan snapshot, and presents action status and source citations.
- `prepare_proposal_draft` is an allowlisted local action. It writes a reviewable Markdown draft and an append-only event with a SHA-256 evidence hash. Missing profile facts remain explicit placeholders.
- Offline demo mode remains advisory and does not fabricate actions or market evidence. Optional API web search is off by default; when enabled, URL citation annotations are captured with the plan.
- Marketplace submission is marked `CAPABILITY_MISSING`; APIP does not ask the owner to approve an action it cannot perform. A public-listing action is also blocked until a direct permitted source executor is registered; API web-search citations alone do not mark a listing as qualified.
- Spending is blocked until the opening balance is verified and the specific amount is within an explicit owner limit. An unknown ledger is not treated as zero.
- Contract acceptance and money movement are `OWNER_HANDOFF` actions.
- Unsupported action types fail closed. No action reports payment as verified.

## Current limits

No marketplace submission, direct web-research, communication, spending, contract, or payment adapter is registered. The optional Responses API can suggest structured steps and supply source citations, but APIP does not independently verify eligibility, keep the API token budget, or calculate API costs. Consequently, this release can execute local draft preparation only; it cannot submit the first commercial application. Paid API calls remain disabled unless explicitly enabled in the local environment.

The next integration should add a permitted public-source research adapter and a verified marketplace action adapter. Surface a scoped approval only after an action is technically available and immediately before the external side effect. Preserve evidence from source retrieval, owner approval, submission receipt, contract, delivery, and payment as separate events.

## Verification

Run `python -m unittest discover -s tests -p test_apip_workflow.py -v`. The suite checks that generated objectives do not authorize outreach, local drafts preserve unverified facts as placeholders, spend and legal actions fail closed, and only allowlisted local work can execute.
