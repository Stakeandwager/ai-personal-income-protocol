# APIP Autonomous Money-Making Mode (AMM)

**Status:** Proposed v1
**Default spending limit:** NGN 0
**Real-money betting and automatic transfers:** Disabled

## 1. Mission

When an authorized agent claims an approved income task, it enters a bounded execution cycle designed to produce a useful deliverable and test a legitimate path to income.

The system must distinguish activity from results. A completed task is not necessarily a sale, and a predicted result is not income.

## 2. Activation

An agent may enter AMM only when a task is explicitly approved and labelled `apip:income-task`.

Pulling the repository alone does not authorize spending money, contacting customers, publishing offers, accessing private accounts, or moving funds.

Every task must specify:
- Task ID and objective
- Intended customer and problem
- Deliverable and deadline
- Proposed revenue path
- Allowed tools and actions
- Success and failure criteria
- Cost ceiling, defaulting to zero
- Actions requiring owner approval

Incomplete tasks must be rejected or paused.

## 3. Execution lifecycle

`QUEUED â†’ CLAIMED â†’ PLAN_RECORDED â†’ EXECUTING â†’ EVIDENCE_RECORDED â†’ REVIEW_REQUIRED`

Possible terminal outcomes:

`VERIFIED_SUCCESS`, `VERIFIED_FAILURE`, `BLOCKED`, or `EXPIRED`.

Every run records its UTC timestamps, task ID, run ID, commit SHA, test results, evidence references, and next action.

Retries must not duplicate external actions.

## 4. Autonomous actions permitted by default

- Inspect approved project files.
- Research using permitted free sources.
- Draft code, analyses, prototypes, and commercial offers.
- Run tests and safe simulations.
- Record progress and results.
- Commit project changes within granted repository permissions.
- Produce an auditable run report.

## 5. Owner approval required

Explicit approval is required before spending money, subscribing to services, sending external messages, publishing commercial offers, accepting contracts, accessing private customer data, changing security permissions, or initiating financial transactions.

No paid APIs or subscriptions without approval of the specific provider, purpose, amount, and duration.

AMM v1 must not place real-money bets, execute speculative trades, or transfer funds automatically.

Never put bank details, passwords, private keys, or access tokens in Git history, issues, or logs.

## 6. Income evidence

Record these as separate states:

- `WORK_COMPLETED`: A deliverable exists and evidence is attached.
- `OFFER_MADE`: An approved offer was sent or published.
- `CUSTOMER_COMMITTED`: A customer accepted the stated terms.
- `PAYMENT_REPORTED`: Payment is claimed but unverified.
- `PAYMENT_VERIFIED`: Payment evidence has been checked with owner approval.
- `REFUND_OR_CHARGEBACK`: Payment was returned or reversed.

Predictions, simulated revenue, clicks, likes, and unpaid invoices must never be counted as earned income.

Reports must separate gross receipts, fees, refunds, and net receipts. No profit is guaranteed.

## 7. Run report

Each run must report its status, objective, actions, changed files, test results, evidence links, commit SHA, costs, approval requests, and next action.

A run that achieves nothing must say so. Do not create meaningless commits merely to show activity.

## 8. GitHub Actions limitation

Scheduled GitHub Actions can run the scripts and tests encoded in the repository while the workflow is enabled and runners are available. A schedule alone is not an autonomous reasoning agent and does not guarantee customer acquisition or income.

A real AI agent requires a configured execution environment, appropriate tools, and narrowly scoped permissions. External actions remain gated by this protocol.

## 9. Acceptance tests

- Incomplete tasks are rejected clearly.
- Unapproved spending and real-money actions are blocked.
- Each run creates an auditable report.
- Simulated and predicted amounts are never reported as income.
- Duplicate task/run IDs cannot repeat side effects.
- Passing tests never implies that revenue has been earned.
- The football predictor remains analysis-only unless separately reviewed and approved.
