# APIP Revenue Protocol v1.0

**Status:** Proposed operating protocol  
**Purpose:** Move APIP from opportunity hypotheses to evidence-backed customer transactions.  
**Owner-authorized cumulative project cap:** USD 1,000 total, including prior APIP spending. **Live spending status:** BLOCKED until the opening balance is independently evidenced and currency-aware hard-stop controls are implemented and validated.  
**Current verified income:** NGN 0 unless the ledger contains independently verifiable receipt evidence.

## 1. Governing rule

APIP must optimize for verified customer value and verified receipts—not for ideas generated, messages sent, reports produced, or tests passed. Each cycle must either advance one real opportunity to the next evidence gate or state what evidence is missing and choose a corrective action.

A hypothesis is not demand. A prospect is not a customer. A positive reply is not an order. An order is not received income. Never fabricate, infer, or double-count evidence.

## 2. Safety and authority

1. The owner has authorized autonomous spending within a maximum cumulative APIP project cap of USD 1,000, including prior APIP spending, but real spending remains blocked until the cumulative opening balance is independently evidenced and currency-aware hard-stop controls are implemented and validated. Once those conditions pass, only lawful, necessary, one-off APIP project expenses within the evidenced remaining balance are in scope; no borrowing, betting, speculative trading, recurring auto-renew subscriptions, or commitments beyond the cap.
2. No external messages, bulk outreach, public offer, account creation, contract, purchase, or payment action without explicit owner approval for the relevant action and scope.
3. Use relevant, truthful, individualized outreach only. Do not use deceptive identities, false claims, evasion tactics, scraped sensitive data, or repeated unwanted contact. Respect platform terms, applicable law, opt-outs, and contact limits.
4. Do not claim credentials, case studies, results, or delivery capability that have not been verified.
5. Do not collect unnecessary personal data. Store only what is needed to manage the experiment and evidence.
6. The owner retains authority over external commitments, pricing exceptions, external publication, and money movement. The scoped USD 1,000 cumulative spending authorization is the only exception to per-expense approval, and it becomes executable only after the documented balance and validated hard-stop prerequisites pass. APIP may prepare drafts and recommendations; preparation is not authorization.
7. Do not treat an AI-generated record, screenshot, or self-reported result as independent proof by itself.

## 3. The seven-stage revenue loop

### Stage 0 — Confirm the system is healthy

- Run the full test suite and income-ledger validation.
- Record the current commit, test result, and known blockers.
- If the test suite fails, fix or clearly isolate the defect before trusting automated reports.
- Keep engineering health separate from commercial progress.

### Stage 1 — Discover observable problems

Generate a small set of problem hypotheses. Each hypothesis must name:

- a specific customer type reachable without paid access;
- a concrete task or pain, not a broad industry trend;
- evidence that the problem exists (public request, repeated complaint, manual workaround, job/task listing, or direct conversation);
- the current workaround and its likely cost in time, money, delay, or risk;
- a small deliverable APIP can realistically produce;
- a plausible buyer and payment route.

Do not select an opportunity solely because APIP can build a tool for it. Prefer problems where a buyer already spends time or money, has a deadline, or actively seeks help.

### Stage 2 — Rank and select one experiment

Score each candidate from 0–2 on: evidence of pain, buyer reachability, urgency, ability to deliver, credible proof, and plausible willingness to pay. Record the evidence behind each score. Select one candidate with the strongest evidence; do not treat the score as proof of demand.

Reject candidates that require upfront spending, unsupported claims, regulated services outside the owner's competence, or access that is unavailable.

### Stage 3 — Build a minimum proof sample

Create one small, honest example of the proposed deliverable using public or owner-provided non-sensitive data. It must be useful enough to evaluate but small enough to produce at zero cost. Include:

- what the buyer receives;
- what is and is not included;
- turnaround estimate;
- a proposed test price and the basis for it;
- a simple acceptance criterion;
- limitations and a correction policy.

Do not build a full product before evidence supports it.

### Stage 4 — Validate the problem with real people

Prepare a list of up to 10 relevant prospects or conversation targets from lawful, publicly available sources or owner-provided contacts. Record why each target is relevant. The owner reviews and explicitly approves the target list and message before any external contact.

Ask about the buyer's current workflow, frequency of the problem, consequences, existing alternatives, and how they currently pay to solve it. Avoid leading questions such as “Would you buy my idea?” Record direct evidence separately from interpretation. Respect no replies, refusals, and opt-outs; do not continue unwanted follow-ups.

**Initial validation threshold:** seek at least 5 substantive conversations or equivalent direct evidence. If fewer are available, report the limitation rather than inventing a conclusion. Stronger evidence includes a buyer sharing a real sample, requesting a quote, agreeing to a paid pilot, or placing an order.

### Stage 5 — Make a specific paid offer

Only after the problem has evidence, prepare an offer for owner approval. It must state the deliverable, scope, price, turnaround, payment terms, acceptance criteria, and correction/refund boundaries. No false scarcity, misleading guarantees, or hidden conditions.

The owner approves sending the offer. Track sent, viewed if verifiable, replied, declined, requested changes, accepted, and paid as separate statuses.

### Stage 6 — Deliver and verify

Deliver only within the agreed scope. Record the agreed order, completion evidence, buyer acceptance or dispute, payment amount, currency, date, and receipt evidence. Count revenue as verified only when the actual receipt is supported by reliable evidence and reconciled against the ledger. Separate gross receipts from fees, costs, refunds, and net income.

Never store full card numbers, passwords, or unnecessary banking credentials. Never claim a transaction was completed based solely on a draft, promise, invoice, or screenshot that cannot be verified.

### Stage 7 — Learn, decide, and automate

After each experiment, record one terminal result:

- `TESTED_DEMAND`: credible evidence of a real problem and buyer commitment; state exactly what evidence exists.
- `TESTED_NO_DEMAND`: the defined test was completed and the specified threshold was not met.
- `ABANDONED_WITH_REASON`: the test could not or should not be completed; state why.

A terminal label does not itself mean money was earned. Preserve source references and append events; never overwrite history to make results look better.

Automate a step only after it has been repeated successfully and its rules are clear. Automate research organization, draft preparation, reminders, deduplication, and evidence summaries before automating external actions. Keep approval gates for outreach, commitments, spending, and money movement.

## 4. Minimum experiment record

Every experiment must include:

- unique experiment ID and selected opportunity ID;
- target customer and problem statement;
- evidence sources with dates;
- score and reason for selection;
- sample deliverable reference;
- target list and owner-approval status;
- approved message/offer version;
- counts for prospects identified, approved, contacted, substantive replies, validated problems, offers, orders, completed deliveries, disputes, and verified receipts;
- cost (default zero), currency, and evidence;
- result, limitations, next action, and responsible person.

Use `data/experiment-events.jsonl` as append-only history if compatible with the current schema. Do not silently change existing event formats; document any schema migration and add tests first.

## 5. Decision rules

- **No credible pain evidence:** return to discovery; do not scale outreach.
- **Pain exists but no buyer can be reached:** revise the target segment or channel.
- **Conversations occur but no one accepts an offer:** examine urgency, trust, proof, scope, and price before changing the entire idea.
- **A buyer accepts but delivery fails:** stop prospecting temporarily and fix delivery quality.
- **Delivery succeeds but payment is not received:** record the receivable as unpaid, not income; follow the agreed terms and do not claim success.
- **One paid pilot succeeds:** ask for feedback and permission to use a testimonial or anonymized case study; do not assume repeatability.
- **Several similar transactions succeed:** standardize the delivery checklist and then automate the repeatable parts.

## 6. First execution cycle

1. Restore a green, trustworthy test run and record the commit and test output.
2. Review the current selected opportunity, `APIP_PROTOCOL_SETUP`. Treat it as an unvalidated hypothesis, not the default answer.
3. Compare it against at least two concrete service hypotheses that can be sampled at zero cost and delivered with existing skills/tools.
4. Choose one segment and one problem using evidence, not convenience.
5. Build one small sample and a clear fixed-scope pilot offer.
6. Prepare up to 10 qualified prospects and one personalized message per prospect. Stop for owner review before any message is sent.
7. Review replies and evidence; decide whether to refine, offer a paid pilot, or abandon the hypothesis.
8. Record outcomes and update the next-action report. Do not automate outbound contact until the manual experiment has demonstrated a compliant, repeatable path.

## 7. Success definition

The first milestone is not “workflow passed.” It is:

1. a real buyer's problem supported by direct evidence;
2. a clearly scoped offer accepted by that buyer;
3. work delivered to the agreed acceptance criteria;
4. payment actually received and verified;
5. the result recorded truthfully with evidence.

Until all five are evidenced, report the exact stage reached and keep verified income at NGN 0 / not established. The USD 1,000 spending authorization is a ceiling, not available cash; missing opening-balance or conversion evidence must block real spending.
