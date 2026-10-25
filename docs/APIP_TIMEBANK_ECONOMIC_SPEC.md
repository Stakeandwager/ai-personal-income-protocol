# APIP TimeBank — Hybrid Economic Specification

**Status:** Proposed, test-only implementation. No real payment feature is enabled.
**Funding model:** Hybrid: subscription revenue and other verified business income.
**Free installation:** Installing the extension is free. Subscription and reward eligibility are separate conditions. Subscription does not guarantee income.

## Funding rules
Only received, reconciled, unrestricted funds explicitly allocated to rewards may enter a pool. Pending invoices, projections, pledges, restricted funds, and reversed transactions are excluded. Approved deductions are applied only within the relevant currency. Currency pools are never combined without an explicitly approved conversion record.

For a currency and period: distributable pool = max(0, verified reward-designated funds − approved deductions and reserves). The initial engine accepts the resulting funding entries and approved deductions as inputs; it does not independently verify bank evidence.

## Reward calculation
For each eligible subscriber: reward = pool × subscriber eligible points ÷ total eligible points. Monetary allocations use integer minor units and a deterministic largest-remainder method. Ties are resolved by subscriber ID. The total allocation must equal the pool when there are positive eligible points and a positive pool; otherwise allocations are zero. One point per eligible minute is a provisional test assumption, not a validated commercial rate or proof of value.

## States
ESTIMATED, FUNDED, APPROVED, PAID, ON_HOLD, DISPUTED, CANCELLED. The initial MVP may calculate estimates from synthetic data; it must not imply any amount is legally owed. No transfer or payment integration is implemented.

## Limits
A timer does not prove attention, playback, completion, or commercial value. This calculation engine does not establish the authenticity of evidence or the legal classification of APIP. Terms, company authority, tax/accounting treatment, privacy obligations, and relevant regulatory questions require review before subscriptions are solicited or payments are promised.
