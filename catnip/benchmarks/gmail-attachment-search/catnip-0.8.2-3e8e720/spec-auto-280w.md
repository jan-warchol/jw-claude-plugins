# Gmail Attachment Search Script

## Goal

CLI tool to find Gmail messages with attachments matching a search query. Useful for quickly
locating emails with files (invoices, reports, etc.) without opening a browser.

## Requirements

- Accepts a Gmail search query string as a CLI argument (same syntax as Gmail's search box)
- Returns the 3 most recent matching emails that have at least one attachment
- For each result, displays: subject, sender, date, and list of attachment filenames with sizes
- Output is human-readable, printed to stdout
- Authenticates via OAuth2/Gmail API; stores credentials locally so re-auth is not needed on
  subsequent runs
- First run opens a browser for one-time authorization; thereafter runs non-interactively

Out of scope: downloading attachments, pagination beyond 3 results, modifying emails.

## Solution

- Use `google-api-python-client` and `google-auth-oauthlib` libraries
- OAuth2 flow with `credentials.json` (from Google Cloud Console) and cached `token.json`
- Call `users.messages.list` with the user query plus `has:attachment` appended, then fetch full
  message metadata for the top 3 results via `users.messages.get` (format: `metadata`)
- Parse `MIME-Version` parts from the message payload to extract attachment names and sizes
- Print results as a simple formatted block per email

**Setup required by user:** create a Google Cloud project, enable Gmail API, download
`credentials.json` (OAuth Desktop app credentials), place it alongside the script.

## Unknowns

- **Attachment size accuracy:** `metadata` format exposes part sizes but may omit them for some
  MIME encodings; fallback to "unknown size" if absent.
- **Query result count:** if fewer than 3 emails match, return however many exist without error.
- **Token refresh:** handled automatically by the Google client library; edge case of revoked
  credentials requires re-running the OAuth flow manually.
