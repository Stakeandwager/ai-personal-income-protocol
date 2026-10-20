# APIP first real income-sourcing experiment — 2026-10-20

## Decision

**Advance a fixed-scope spreadsheet cleanup service toward one live marketplace proposal.** The best current lead is a public Upwork buyer brief for Excel/database cleanup. The listing showed a US$10 fixed budget, 20–50 proposals, one hire, 16 active hires on the buyer profile, and US$4.2K previously spent. This is evidence that a buyer posted a scoped request and has prior platform activity; it does not prove that this buyer will hire APIP or that the task remains open. The indexed page reported a recent post/view, but full listing retrieval returned 403, so the page details were not independently reloaded.

**Offer to test:** clean up to 100 client-supplied rows for **US$10 fixed price**, return a normalized CSV and exceptions/QA notes, within 24 hours of receiving the file and agreed deduplication rules, with one clarification pass. Estimate: 1–2 hours. No guessing, contact enrichment, or changes to the original file. Work only after an appropriately funded fixed-price milestone. Upwork's current fee is shown per contract and ranges from 0% to 15%; the exact take-home cannot be calculated until a proposal/offer shows the rate. Proposal Connects vary by job and can require paid credits; the exact amount and free balance are unknown.

**Proposal draft (not sent):** “I can clean and standardize up to 100 rows from your supplied Excel/Sheets export, remove confirmed duplicates, and return a cleaned CSV plus a short exceptions log for missing or conflicting values. I will preserve your original file and will not guess missing information. For US$10, I can deliver within 24 hours after we confirm the row limit, deduplication key, and required output columns. Please confirm the dataset size and whether you want ambiguous records held for review.” This draft makes no claim of past client work or results.

**Next executable action:** a human with an authorized Upwork freelancer account must open the listing, confirm it remains open and eligible, review the sample at `examples/spreadsheet-cleanup-demo-v1/`, check the displayed Connects charge against the evidenced opening expense balance, and submit the prepared offer only if it requires no new spending or the ledger/authorization permits it. No bid, purchase, or external contact was made in this run.

## Five ranked opportunities

Ranks reflect visible buyer activity, alignment with current local capability, low-cost delivery, and barriers to reaching the buyer—not estimated probability of a sale.

| Rank | Opportunity and observed demand evidence | Skills / estimated delivery | Payment route | Upfront cost estimate and risks |
|---|---|---|---|---|
| 1 | **Excel/database cleanup.** Upwork listing posted recently: US$10 fixed price; 20–50 proposals; one hire; buyer profile showed US$4.2K spent, 269 hires, 16 active. [Listing](https://www.upwork.com/freelance-jobs/apply/Excel-Data-Entry-Database-Cleanup-Specialist_~022107542558398603922/) | Excel/Sheets, careful normalization, deduplication, QA, client communication. Estimate 1–2 hours for a bounded 100-row sample; more for large datasets. | Upwork fixed-price contract/milestone; fund before starting, release after client acceptance. | Essential software: NGN 0 using local CSV/Python tools. Applying may consume Connects; job-specific amount and account balance unknown. Risks: high competition, scope creep, conflicting records, privacy of client files, listing status cannot be reloaded (403). |
| 2 | **Web research plus spreadsheet building.** Current Upwork post: US$10 fixed price; 50+ proposals; one hire; buyer showed US$599 spent, 56 hires, 3 active. [Listing](https://www.upwork.com/freelance-jobs/apply/Data-Entry-Web-Research-Expert-Excel-Google-Sheets_~022111403098525592917/) | Public-source research, source URLs, data validation, spreadsheet formatting, deduplication. Estimate 2–4 hours for 25 verified business rows, dependent on sources and fields. | Upwork fixed price, escrow/milestone release. | NGN 0 for public research and local CSV processing; Connects may cost money. Risks: 50+ proposals, undefined volume, freshness/accuracy expectations, contact-data and platform-policy limits. |
| 3 | **Five Canva social posts.** Current post: US$10 fixed price, 10–15 proposals, one hire; buyer located in Nigeria and showed US$173 spent and 16 hires. [Listing](https://www.upwork.com/freelance-jobs/apply/Canva-Designer-Needed-for-Social-Media-Design-for-Instagram-and-Facebook_~022111135026222001097/) | Canva, layout, brand consistency, accessible text and editable file delivery. Estimate 2–4 hours if account/assets are supplied. | Upwork fixed price, milestone acceptance/release. | Canva connector/account not installed; use may incur credits or subscription (unpriced, not authorized). Risks: portfolio skill not evidenced, assets/licensing, revisions may exceed $10. |
| 4 | **One Instagram review, Canva post and caption.** Current post listed US$5, 10–15 proposals, one hire, and buyer showed US$15 spent and 7 hires. [Listing](https://www.upwork.com/freelance-jobs/apply/Social-Media-Manager-Needed-for-Instagram-Content-Posting_~022106378201411826059/) | Social content audit, Canva, caption/hashtag writing. Estimate 1–2 hours. | Upwork fixed price. | NGN 0 only if no paid design account; Upwork Connects possible. Risks: low gross budget, subjective approval, social account posting access not provided, this research task has no publishing channel. |
| 5 | **Product-focused Shopify technical article.** Fresh post advertises four 1,500–2,000-word articles/month for US$200 total, with real app walkthroughs, screenshots, and original analysis; indexed result showed 15–20 proposals and two interviews. [Listing](https://www.upwork.com/freelance-jobs/apply/Technical-Content-Writer-for-Shopify-App-Blog_~022103381467300047165/) | Strong English technical writing, Shopify app use, product research, screenshot capture, editorial QA. Estimate 20–32 hours/month. | Upwork fixed-price monthly scope or milestones, terms to confirm. | NGN 0 if app access is free, but access may require a paid subscription (unknown). Risks: steep experience requirement, product/account access, originality and accuracy, large time requirement, low effective hourly rate. |

### Evidence quality notes

- The listings above are indexed public Upwork job pages surfaced by current search on 2026-10-20. Their descriptions, budget, proposal counts, and client summaries were visible in search results. Opening the individual Upwork pages returned HTTP 403, so no authenticated account state, current open/closed status, client identity, or final hire outcome was independently confirmed.
- Proposal counts and client hire/spend figures are platform-displayed claims, not proof of completed successful delivery or payment to APIP.
- The listings show expressed buyer intent and marketplace competition. They do not establish general market size, a sale probability, local Nigerian demand, or APIP-specific willingness to pay.
- Upwork help says freelancer fees vary from 0% to 15% per contract and are displayed at proposal/offer time. Fixed-price work uses funded milestones/escrow, and Connects required vary per job. Sources: [service fee](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee), [fixed-price milestones](https://support.upwork.com/hc/en-us/articles/17931377993107--Decide-between-hourly-and-fixed-price-contract), [Connects](https://support.upwork.com/hc/en-us/articles/211062898-Understanding-and-using-Connects).

## Work completed locally

- Inspected README, task queue, project state, decisions, handover, expense-control specification, current test report, income ledger, opportunity-engine code/output, and lock status before adding anything.
- Confirmed local tests/results and income report were pre-existing evidence: prior suite 47 passed; ledger has 0 rows; last protocol run had 0 income records. No new test suite was run because this run added documentation and a fictional CSV example, not executable code.
- Searched current public buyer listings and current official Upwork payment/fee/Connects guidance.
- Searched connected-app catalog for outreach/CRM, marketplace, and publishing. No Upwork connector surfaced; candidate Canva/WordPress/Metricool and email/CRM apps were `installed:false`. Stripe appeared as an uninstalled payment connector. GitHub access listed only `Stakeandwager/genesis`, not the APIP project.
- Created a synthetic spreadsheet cleanup example and recorded privacy/no-secrets market-access rules for APIP.

## Research, verification, attempt, completion, confirmation

| Stage | Result |
|---|---|
| Researched | Five current Upwork job briefs and official fee, fixed-price, and Connects pages. |
| Verified locally | APIP income ledger is empty; cumulative prior experiment spend is not established; no live expense database; no outreach/publishing/purchasing integration is connected; working tree has pre-existing uncommitted changes. |
| Attempted externally | Current search and connector/plugin discovery. Web search worked; Upwork page open was blocked (403). No application or message submission was attempted because no connected Upwork account/recipient workflow exists. |
| Completed | Local offer specification, proposal-ready sample, ranked evidence report, and safe outreach/privacy policy. |
| Independently confirmed | No buyer response, contract, delivery, or payment. Revenue remains zero/unestablished. No money was spent. |

## Budget and blockers

- Cash spent this run: **NGN 0**.
- Actual cumulative prior APIP spend/opening balance: **unknown and not initialized**. Therefore the authorized cumulative NGN 10,000 ceiling has no evidence-backed remaining-balance figure. No Connects purchase or other spend is permitted before reconciliation and ledger initialization.
- Upfront software cost for the spreadsheet demo: **NGN 0** using local tools. Marketplace bid cost: **unknown** until the account shows job-specific Connects and balance. Exact freelancer fee: **0–15% per Upwork's current page**, to be disclosed on a contract/proposal.
- External execution blocker: no installed/authenticated Upwork freelancer account or connected application tool; no confirmed eligible account, Connects balance, payout method, or listing open status.
- Safety blocker for independent outreach: no connected APIP-owned publication/mail/CRM and no vetted target-recipient list. Never transmit account/payment details or secrets as marketing content.

## Success condition for the next experiment

The experiment is successful only when all of these occur: (1) one currently open, relevant buyer opportunity is confirmed; (2) a proposal is submitted with **zero new cash spend** unless a source-backed opening ledger and authorized Connects spend allow otherwise; (3) the buyer funds a fixed-price milestone; (4) the bounded deliverable is submitted and accepted; and (5) a released payment is evidenced by an independent platform transaction record or payout receipt and entered in APIP with fees/costs separated. A posted job, submitted proposal, positive reply, or contract amount alone does not count as revenue.

## Preserve and handoff

Existing user changes were preserved; no commit or push was made. Continue by checking whether the owner has reconciled prior cumulative spend and connected an authorized marketplace account. If those are ready, verify the candidate listing is still open and submit the offer only after reviewing the displayed Connects requirement and fee.
