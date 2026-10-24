# Sample QA notes

- Input records: 5.
- Cleaned records: 1.
- Exception records: 4.
- Exact duplicates removed: 1.
- Duplicate handling: `company`, `contact_name`, and `email` are the agreed demo keys. One repeated Blue River Books row matched exactly after approved trimming and formatting and was removed. The Northstar records share case-insensitive keys but differ in contact/phone values; both were withheld. Unknown Store has missing key values and a non-phone value in the phone field; it was withheld for review. See `engine-output/exceptions-input-demo-only.csv`.
- Formatting: email domain case is lowercased while its local part is preserved. Phone separators are removed while digits are retained; no country code or national format is inferred. Malformed selected values are routed to the exceptions file.
- Mapping: `engine-output/mapping-guide-input-demo-only.csv` shows proposed source-to-target mappings and explicitly requires buyer confirmation. A production mapping must use the buyer's actual import template and required fields.
- Missing data: Unknown Store has no contact name or email. No values were guessed, enriched, or silently repaired.
- Quality limitation: These are fictional rows using reserved `.invalid` example addresses. There is no external source validation and no real business data. The tool handles CSV only and has not been exercised on a client's data or an `.xlsx` workbook.

For an actual delivery, preserve the original and a before/after copy, get written agreement on dedupe keys, mapping targets, and email/phone rules, maintain an exceptions file, and validate row counts and transformations before sending the result.
