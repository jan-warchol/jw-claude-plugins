# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the three most recently received emails matching that query that contain at least one attachment. "Most recent" is defined by Gmail's default message ordering (newest-first by received date).

---

## Setup

### Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Install via: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### Google Cloud Configuration

1. Create a project in Google Cloud Console.
2. Enable the Gmail API.
3. Create OAuth 2.0 credentials (Desktop app type) and download `credentials.json`.
4. Place `credentials.json` in the same directory as the script.
5. Run the script; a browser window will open for first-time authorization.

### Authentication and Credentials

- Scope: `https://www.googleapis.com/auth/gmail.readonly`
- On first run, an OAuth consent flow opens in the browser. The resulting token is cached in `token.json` and reused on subsequent runs. Expired access tokens are refreshed automatically using the stored refresh token.
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

The search query is taken from `sys.argv[1]` if provided, otherwise prompted via `input()`. It accepts any Gmail search query string (same syntax as the Gmail search box).

### Processing

1. Call `users.messages.list` with the user query. Append `has:attachment` unless it is already present (case-insensitive check), then pass `maxResults=3`. The API returns results newest-first.
2. For each message ID, call `users.messages.get` with `format=metadata` to retrieve headers (`From`, `Subject`, `Date`) and part metadata.
3. Collect attachment filenames by recursively walking `payload.parts` and selecting parts where `filename` is non-empty. Inline images (`Content-Disposition: inline`) are excluded; only true file attachments are listed.

### Output

Print a numbered summary to stdout for each of the (up to) 3 emails:

```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   Attachments: <filename1>, <filename2>, ...

2. ...
```

If no matching emails with attachments are found, print: `No emails with attachments found for query: "<query>"`

### Error Handling

- Missing `credentials.json`: print a clear message pointing to setup instructions and exit.
- API errors (e.g., invalid query, quota exceeded): catch `googleapiclient.errors.HttpError`, print the error message, and exit with a non-zero code.
- Fewer than 3 matching emails: return however many exist without error.

---

## Design Choices

- **Gmail API over IMAP:** The Gmail API returns rich structured metadata (headers, MIME parts) without downloading full message bodies, keeping the script fast and simple. IMAP would require manual MIME parsing and is more verbose.
- **Server-side `has:attachment` filter over client-side:** Delegating attachment filtering to the API avoids fetching pages of results that would be discarded, which matters given Gmail's daily quota limits (~1 billion units/day for free projects, with `messages.list` and `messages.get` each costing 5 quota units per call).
- **`format=metadata` over `format=full`:** Fetching only headers and part structure avoids transferring base64-encoded attachment bodies, which can be large.

---

## Assumptions and Exclusions

**Assumptions:**
- The Gmail account being queried belongs to the user running the script (uses `userId="me"`).
- A standard browser is available for the first-time OAuth consent flow.

**The script does NOT:**
- Download or save attachment content to disk.
- Paginate beyond the first 3 results.
- Decode or display email body text.
- Support multiple Gmail accounts simultaneously.
- Provide any GUI or web interface.
