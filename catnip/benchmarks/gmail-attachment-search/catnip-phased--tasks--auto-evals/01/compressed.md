# Gmail Attachment Search — Spec

## Overview

CLI Python script: authenticate with Gmail via OAuth2, accept a user-provided search query, and print the 3 most recently received matching emails that have attachments (newest-first by received date).

---

## Setup

### Dependencies

`pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### Google Cloud Configuration

1. Create a Google Cloud project and enable the Gmail API.
2. Create OAuth 2.0 credentials (Desktop app type); download as `credentials.json`.
3. Place `credentials.json` next to the script and run it — a browser window opens for first-time authorization.

### Authentication and Credentials

- Scope: `https://www.googleapis.com/auth/gmail.readonly`
- First run opens an OAuth browser flow; token is cached in `token.json` and auto-refreshed on expiry.
- `credentials.json` must be a Desktop-type OAuth2 client secret (not a service account key).

### File Structure

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (user-provided, not committed)
token.json                   # cached token (auto-generated, not committed)
```

---

## Behavior

### Input

Query: `sys.argv[1]` or `input()` prompt. Accepts any Gmail search syntax.

### Processing

1. Call `users.messages.list` with the query (append `has:attachment` if absent, case-insensitive) and `maxResults=3`; results are newest-first.
2. For each message ID, call `users.messages.get` with `format=metadata` to fetch headers (`From`, `Subject`, `Date`) and part metadata.
3. Collect filenames by recursively walking `payload.parts` where `filename` is non-empty; exclude inline images (`Content-Disposition: inline`).

### Output

```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   Attachments: <filename1>, <filename2>, ...

2. ...
```

If no results: `No emails with attachments found for query: "<query>"`

### Error Handling

- Missing `credentials.json`: print setup instructions and exit.
- `HttpError` from the API: print the error message and exit non-zero.
- Fewer than 3 matches: return however many exist.

---

## Design Choices

- **Gmail API over IMAP:** API returns structured metadata without downloading bodies; IMAP requires manual MIME parsing.
- **Server-side `has:attachment` filter:** Avoids fetching pages of results only to discard them; `messages.list` and `messages.get` each cost 5 quota units.
- **`format=metadata` over `format=full`:** Avoids transferring base64-encoded attachment bodies.

---

## Assumptions and Exclusions

**Assumptions:**
- Queries the authenticated user's own account (`userId="me"`).
- A browser is available for the first-time OAuth flow.

**The script does NOT:**
- Download attachment content to disk.
- Paginate beyond 3 results.
- Decode or display email body text.
- Support multiple Gmail accounts or provide a GUI.
