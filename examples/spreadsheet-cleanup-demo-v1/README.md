# Spreadsheet cleanup sample — v1

This is a synthetic demonstration of a small CSV cleanup service. Every company, person, email, and value in the sample is fictional. Do not contact anyone using this data.

## Files

- `input-demo-only.csv`: deliberately inconsistent fictional rows.
- `cleaned-demo-only.csv`: refreshed cleaned output from the local cleanup script.
- `exceptions-demo-only.csv`: refreshed record-level conflicts, duplicates, and malformed/missing values.
- `mapping-guide-demo-only.csv`: proposed CRM field crosswalk, with buyer confirmation required.
- `engine-output/`: exact output names produced by the documented run command.
- `qa-notes.md`: transformation and quality notes.

Run the demo from the project root:

```powershell
python scripts/spreadsheet_cleanup.py examples/spreadsheet-cleanup-demo-v1/input-demo-only.csv --key-columns company contact_name email --email-columns email --phone-columns phone --target-fields Account_Name Contact_Name Email Phone City --field-map company=Account_Name --field-map contact_name=Contact_Name --field-map email=Email --field-map phone=Phone --field-map city=City --output-dir examples/spreadsheet-cleanup-demo-v1/engine-output
```

The script writes a cleaned CSV, an exceptions CSV, and a field-mapping guide. It trims whitespace, uses agreed keys to find possible collisions, removes a repeat only when every value matches exactly after approved transformations, and withholds conflicting or malformed selected values for review. The opt-in email rule lowercases only the domain and preserves the local part. The opt-in phone rule removes visual separators while preserving digits and an explicit leading `+`; it does not infer country codes. Proposed field mappings remain marked for buyer confirmation, and unmapped target fields are listed as missing. It does not guess corrections, normalize date/number formats, edit Excel workbooks, or preserve formulas. Input files are not changed; existing outputs are protected unless `--force` is supplied.

## Proposed paid scope

Clean up to 100 client-supplied rows in one **CSV file for US$10 fixed price**. Confirm the target columns, deduplication key, and any optional email/phone formatting before processing. Return the cleaned CSV, an exceptions log, and a brief quality note. Delivery target: within 24 hours after receiving a usable file, agreeing the rules, and confirming the fixed-price milestone is funded. One clarification/revision pass within the original scope. No contact enrichment, guessing, web scraping, formula repair, native Excel workbook editing, or changes to the client's source file.

This is a proposed introductory price for one bounded offer, not a market average, accepted quote, or guaranteed sale. Platform fees and proposal Connects may apply. The current target listing and a proposal draft are documented in `offers/spreadsheet-cleanup-buyer-ready-offer-2026-10-24.md`. The listing's status and account eligibility must be confirmed by an authorized freelancer account before submission. No bid has been sent.

## Safety and truth rules

- Retain only the client-provided fields needed for the agreed cleanup.
- Do not invent or infer missing values. Put ambiguous, conflicting, and missing-key records in an exceptions list.
- Do not put bank/payment details, credentials, personal secrets, or client records into public samples, prompts, or logs.
- Work only under a funded platform contract or other agreed payment protection; do not begin an Upwork fixed-price task until its milestone is funded.
- This sample is not evidence of customer demand, a client contract, delivery to a customer, or income.
