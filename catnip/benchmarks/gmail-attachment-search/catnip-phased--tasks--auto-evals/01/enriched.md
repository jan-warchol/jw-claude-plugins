# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the three most recently received emails matching that query that contain at least one attachment. "Most recent" is defined by Gmail's default message ordering (newest-first by received date).

---

## Authentication

- Uses the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- OAuth2 credentials stored in `credentials.json` (downloaded from Google Cloud Console).
- Token cached in `token.json` after first authorization; reused on subsequent runs. The library automatically refreshes expired access tokens using the stored refresh token.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`

---

## Inputs

| Input | Source | Description |
|---|---|---|
| `query` | CLI argument (`sys.argv[1]`) or `input()` prompt | Gmail search query string (same syntax as Gmail search box) |

If the user's query already contains `has:attachment`, the script must not append it a second time (check before appending).

---

## Processing

1. Authenticate and build a Gmail API service object.
2. Append `has:attachment` to the user query unless it is already present (case-insensitive check).
3. Call `users.messages.list` with the combined query and `maxResults=3`; the API returns results newest-first.
4. For each message ID, call `users.messages.get` with `format=metadata` to retrieve headers (`From`, `Subject`, `Date`) and part metadata.
5. Collect attachment filenames from `payload.parts` (recursively, to handle nested MIME parts) where `filename` is non-empty. Inline images (`Content-Disposition: inline`) are excluded; only true file attachments are listed.

---

## Output

Print a numbered summary to stdout for each of the (up to) 3 emails:

```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   Attachments: <filename1>, <filename2>, ...

2. ...
```

If no matching emails with attachments are found, print: `No emails with attachments found for query: "<query>"`

---

## Assumptions and Exclusions

**Assumptions:**
- `credentials.json` is a Desktop-type OAuth2 client secret (not a service account key).
- The Gmail account being queried belongs to the user running the script (uses `userId="me"`).
- A standard browser is available for the first-time OAuth consent flow.

**Explicit exclusions — the script does NOT:**
- Download or save attachment content to disk.
- Paginate beyond the first 3 results.
- Decode or display email body text.
- Support multiple Gmail accounts simultaneously.
- Provide any GUI or web interface.

---

## Design Choices and Trade-offs

- **Gmail API over IMAP:** The Gmail API returns rich structured metadata (headers, MIME parts) without downloading full message bodies, keeping the script fast and simple. IMAP would require manual MIME parsing and is more verbose.
- **Server-side `has:attachment` filter over client-side:** Delegating attachment filtering to the API avoids fetching pages of results that would be discarded, which matters given Gmail's daily quota limits (~1 billion units/day for free projects, with `messages.list` costing 5 units and `messages.get` costing 5 units per call).
- **`format=metadata` over `format=full`:** Fetching only headers and part structure avoids transferring base64-encoded attachment bodies, which can be large.

---

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Install via: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

---

## Setup

1. Create a project in Google Cloud Console.
2. Enable the Gmail API.
3. Create OAuth 2.0 credentials (Desktop app type) and download `credentials.json`.
4. Place `credentials.json` in the same directory as the script.
5. Run the script; a browser window will open for first-time authorization.

---

## Error Handling

- Missing `credentials.json`: print a clear message pointing to setup instructions and exit.
- API errors (e.g., invalid query, quota exceeded): catch `googleapiclient.errors.HttpError`, print the error message, and exit with a non-zero code.
- Fewer than 3 matching emails: return however many exist without error.

---

## File Structure

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (user-provided, not committed)
token.json                   # cached token (auto-generated, not committed)
```
