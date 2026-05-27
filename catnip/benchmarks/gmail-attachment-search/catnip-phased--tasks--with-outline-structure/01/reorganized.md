# Gmail Attachment Search Script — Spec

## Objective

Build a simple Python CLI script that authenticates with Gmail, accepts a search query from the user, and returns the three most recent emails matching that query that contain at least one attachment. This fills a common need for quickly finding recent attachments without manually browsing Gmail.

---

## Requirements

### Must do
- Accept a search query as a command-line argument (or prompt interactively if not provided).
- Authenticate with Gmail using OAuth 2.0 (Google API credentials).
- Search Gmail for messages matching the query and filter to only those with attachments.
- Return the last 3 matching messages (most recent first); display however many exist if fewer than 3 are found.
- For each result, display: subject, sender, date, and attachment filename(s).

### Must not do
- Download or save attachment files to disk.
- Modify, delete, or send any emails.
- Store credentials in plain text (must use OAuth token file or similar safe storage).

---

## Solution

### Setup and authentication

The user must create a Google Cloud project, enable the Gmail API, and download `credentials.json` (OAuth client secret). The script expects this file in the current working directory; if absent, it exits immediately with instructions to download it from the Google Cloud Console.

On first run, the script performs the OAuth 2.0 flow (opens browser) and stores the resulting token in `token.json` in CWD. Subsequent runs reuse the cached token, refreshing it automatically if expired.

Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`. Python 3.8+ assumed.

### Search and retrieval

Call `users.messages.list` with the user-supplied query string. If the query does not already contain `has:attachment`, append it automatically to pre-filter at the API level. Request up to `maxResults=10` (a small buffer to account for edge cases where the API filter over-matches).

`users.messages.list` returns only message IDs. For each candidate, call `users.messages.get` with `format=metadata` (fetches headers and part structure only, avoiding large body payloads) and request headers `Subject`, `From`, `Date`. Parse the `parts` payload to collect attachment filenames (parts where `filename` is non-empty and `body.attachmentId` is set). Take the first 3 messages that have confirmed attachments after local inspection.

### Output and error handling

Print results to stdout in a human-readable format, e.g.:

```
1. Subject: Q3 report
   From: alice@example.com
   Date: Mon, 26 May 2026 10:00:00 +0000
   Attachments: q3_report.pdf, budget.xlsx

2. ...
```

Error behavior:
- **Missing/malformed `credentials.json`**: print setup instructions and exit with a non-zero code.
- **Auth failure / token refresh failure**: print the error and exit. Do not silently retry.
- **API errors** (e.g. quota exceeded, network failure): surface the error message and exit.
- **Zero results**: print "No matching emails with attachments found." and exit with code 0.

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
- API quota management (fetching 3 results is well within free-tier limits).

---

## Uncertainty

- **What counts as an "attachment"**: Gmail's `has:attachment` filter includes inline images. The script should distinguish true file attachments from inline parts (check `attachmentId` being set, or `Content-Disposition: attachment` on the part). Needs validation against real Gmail data.
- **Token and credential file paths**: Both default to CWD for simplicity. Whether these should be configurable via CLI flags or env vars is not specified.
- **Output format**: Plain text assumed; JSON output might be useful for programmatic use but is not requested.
