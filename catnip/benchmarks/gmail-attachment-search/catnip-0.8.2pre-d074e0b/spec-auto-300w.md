# Gmail Attachment Search — Spec

## Goal

CLI script to find the 3 most recent Gmail messages matching a user-supplied query that have at
least one attachment, and print their metadata to stdout. Useful for quickly locating recent
attachments without opening Gmail.

## Requirements

- Accept a Gmail search query as a positional CLI argument.
- Authenticate via OAuth2: read `credentials.json` from the working directory; persist the refresh
  token to `token.json` after first login (subsequent runs are non-interactive).
- Return exactly the 3 most recent matching emails with attachments, ordered newest-first. If
  fewer than 3 exist, return all that do and indicate how many were found.
- Per-email output (stdout): subject, sender, date, and for each attachment: filename and size in
  human-readable units.
- Non-goals: downloading attachments, modifying/labeling messages, pagination UI, async execution.

## Solution

- **Dependencies**: `google-api-python-client`, `google-auth-oauthlib` (standard Gmail API stack).
- **Auth flow**: On first run, open a browser for OAuth2 consent; save token to `token.json`.
  Subsequent runs load and auto-refresh the token silently.
- **Query strategy**: Append `has:attachment` to the user query and request results ordered by
  date descending. Fetch up to ~10 results (Gmail's `has:attachment` filter is reliable, so the
  first few results will have attachments; stop after collecting 3).
- **Single-file script** (`search_attachments.py`); no framework, minimal boilerplate. Required
  OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- **Output format**: plain text, one email block per result, separated by a blank line.

## Unknowns

- **Credentials setup**: user must create a Google Cloud project and download `credentials.json`
  themselves — this is out of scope for the script but should be documented in a usage comment or
  README.
- **Quota**: Gmail API free quota (250 units/second) is far above what this script needs; not a
  practical concern.
- **Edge case**: if the user query itself already contains `has:attachment`, appending it again is
  harmless (Gmail deduplicates).
