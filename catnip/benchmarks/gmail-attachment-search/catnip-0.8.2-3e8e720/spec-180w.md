# Gmail Attachment Finder — Spec

## Goal

Single-file Python CLI script to quickly locate the most recent Gmail messages matching a
user-supplied query that contain attachments, displaying metadata without downloading files.

## Requirements

- Accept search query as a CLI argument: `python script.py "from:boss subject:invoice"`
- Automatically apply `has:attachment` to the query (additive)
- Return the 3 most recent matching messages; if fewer exist, return all with a note
- Output per message: subject, date, sender; per attachment: filename and size
- Non-goals: downloading attachments, paginating deep result sets, modifying messages

## Solution

- Dependencies: `google-api-python-client`, `google-auth-oauthlib`
- Auth: OAuth2 with `credentials.json` in working directory; cache token to `token.json`; scope
  `gmail.readonly`
- Fetch up to ~20 results ordered by date descending; filter to first 3 that have attachments
- Detect attachments by inspecting MIME parts for non-empty `filename` fields
- Print results to stdout in human-readable format; exit with an error message on auth or API
  failure

## Unknowns

- If user includes `has:attachment` manually it will be duplicated — harmless; could deduplicate
  trivially
- Queries matching thousands of messages with no attachments may require fetching multiple pages
  to find 3 — out of scope for a "simple" script; first page only is acceptable
- No size limit specified for "large" attachments in output formatting
