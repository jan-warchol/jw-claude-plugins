# Gmail Attachment Search Script — Spec

## Objective

Build a simple Python CLI script that authenticates with Gmail, accepts a search query from the user, and returns the three most recent emails matching that query that contain at least one attachment. This fills a common need for quickly finding recent attachments without manually browsing Gmail.

---

## Requirements

### Must do
- Accept a search query as a command-line argument (or prompt interactively if not provided).
- Authenticate with Gmail using OAuth 2.0 (Google API credentials).
- Search Gmail for messages matching the query.
- Filter results to only messages that have at least one attachment.
- Return the last 3 matching messages (most recent first).
- For each result, display: subject, sender, date, and attachment filename(s).
- Handle the case where fewer than 3 results are found gracefully (display however many exist).
- Print a clear message if no matching emails with attachments are found.
- Exit with a descriptive error message if `credentials.json` is missing or malformed.

### Must not do
- Download or save attachment files to disk.
- Modify, delete, or send any emails.
- Store credentials in plain text (must use OAuth token file or similar safe storage).

---

## Solution

### Authentication
Use the Gmail API via `google-auth` and `google-api-python-client`. On first run, perform the OAuth 2.0 flow (opens browser) and store the resulting token in a local `token.json` file. Subsequent runs reuse the cached token, refreshing it automatically if expired.

Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

The script expects `credentials.json` (OAuth client secret) in the current working directory. If absent, it exits immediately with instructions to download it from the Google Cloud Console.

### Search
Call `users.messages.list` with the user-supplied query string. If the query does not already contain `has:attachment`, append it automatically to pre-filter at the API level.

Example combined query: `{user_query} has:attachment`

### Fetching message details
`users.messages.list` returns only message IDs. For each candidate, call `users.messages.get` with `format=metadata` (fetches headers and part structure only, avoiding large body payloads) and request headers `Subject`, `From`, `Date`. Parse the `parts` payload to collect attachment filenames (parts where `filename` is non-empty and `body.attachmentId` is set).

### Result limit
Request up to `maxResults=10` from the API (a small buffer), then take the first 3 that have confirmed attachments after local inspection. This handles edge cases where `has:attachment` matches messages with inline images that aren't "real" attachments.

### Error handling
- **Missing `credentials.json`**: print a setup instructions message and exit with a non-zero code.
- **Auth failure / token refresh failure**: print the error and exit. Do not silently retry.
- **API errors** (e.g. quota exceeded, network failure): surface the error message and exit.
- **Zero results**: print "No matching emails with attachments found." and exit with code 0.
- **Fewer than 3 results**: display all found results without error.

### Output
Print results to stdout in a human-readable format, e.g.:

```
1. Subject: Q3 report
   From: alice@example.com
   Date: Mon, 26 May 2026 10:00:00 +0000
   Attachments: q3_report.pdf, budget.xlsx

2. ...
```

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Python 3.8+ assumed (no earlier version compatibility required).

### Credentials setup
The user must create a Google Cloud project, enable the Gmail API, and download `credentials.json` (OAuth client secret). The script looks for this file in the current working directory.

---

## Alternative solutions considered

- **`imaplib` + Gmail IMAP**: No additional SDK needed, but IMAP access requires enabling "less secure apps" or app passwords, is slower for search, and lacks structured attachment metadata. Gmail API is the recommended approach.
- **`simplegmail` third-party library**: Wraps the Gmail API with a friendlier interface, but adds an extra dependency and less control. Not worth it for a simple script.

---

## Out of scope

- Downloading or saving attachments.
- Support for multiple Gmail accounts in one run.
- Pagination beyond the first page of API results.
- Any GUI or web interface.
- Unit or integration tests.
- Packaging as a pip-installable tool.

---

## Uncertainty

- **What counts as an "attachment"**: Gmail's `has:attachment` filter includes inline images. The script should distinguish between inline content-disposition parts and true file attachments (check `Content-Disposition: attachment` header on the part, or rely on `attachmentId` being set). Needs validation against real Gmail data.
- **Token storage location**: Should `token.json` be stored in CWD, `~/.config/`, or alongside the script? Not specified; defaulting to CWD for simplicity.
- **Credential file path**: Should `credentials.json` be configurable via a CLI flag or env var, or always expected in CWD?
- **Output format**: Plain text assumed; JSON output might be useful for programmatic use but not requested.
- **Rate limits**: For a simple 3-result script, API quota is not a concern in practice.
