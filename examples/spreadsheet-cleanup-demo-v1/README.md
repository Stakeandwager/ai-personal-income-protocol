# Spreadsheet cleanup sample — v1

This is a synthetic demonstration of a small spreadsheet cleanup service. Every company, person, email, and value in the sample is fictional. Do not contact anyone using this data.

## Files

- `input-demo-only.csv`: deliberately inconsistent fictional rows.
- `cleaned-demo-only.csv`: normalized output; exact duplicate removed.
- `exceptions-demo-only.csv`: ambiguous or incomplete records to confirm.
- `qa-notes.md`: transformation and quality notes.

## Proposed paid scope

Clean up to 100 client-supplied rows for **US$10 fixed price**: normalize whitespace and casing where safe, standardize phone formatting only when unambiguous, remove exact duplicate rows, preserve original facts, and return a cleaned CSV plus an exceptions log. Delivery estimate: within 24 hours after receiving a usable file and agreed field rules (estimated 1–2 hours of work). One clarification/revision pass. No contact enrichment, guessing, or changes to the client's source file.

The price is anchored to a live Upwork listing that displayed a US$10 fixed-price budget; it is a proposed test price, not a market average or guaranteed acceptance. Upwork service fees and proposal Connects apply as shown by Upwork at the time. No bid has been sent.

## Safety and truth rules

- Retain only the client-provided fields needed for the agreed cleanup.
- Do not invent or infer missing values. Put ambiguous records in an exceptions list.
- Do not put bank/payment details, credentials, personal secrets, or client records into public samples, prompts, or logs.
- Work only under a funded platform contract or other agreed payment protection; do not begin an Upwork fixed-price task until its milestone is funded.
- This sample is not evidence of customer demand, a client contract, delivery to a customer, or income.
