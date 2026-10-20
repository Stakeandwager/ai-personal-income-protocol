# Sample QA notes

- Input rows: 5.
- Output rows: 2.
- Duplicate handling: one normalized exact duplicate removed (Blue River Books). The Northstar rows share a normalized company/contact/email but disagree on phone; both were withheld pending client confirmation. See `exceptions-demo-only.csv`.
- Normalization: trimmed whitespace and title-cased company/contact/city labels; lowercased email addresses; kept phone values unchanged when formats were ambiguous.
- Missing data: Unknown Store has no contact details. The company label is retained and the row is flagged. No values were guessed or enriched.
- Quality limitation: These are fictional rows using reserved `.invalid` example addresses. There is no external source validation and no real business data.

For an actual delivery, preserve a before/after copy, define dedupe keys with the client, maintain an exceptions file, and validate counts and transformations before sending the result.
