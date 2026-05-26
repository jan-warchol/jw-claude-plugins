# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the three most recent emails matching that query that contain at least one attachment.

---

## Authentication

- Uses the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- OAuth2 credentials stored in `credentials.json` (downloaded from Google Cloud Console).
- Token cached in `token.json` after first authorization; reused on subsequent runs.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`

---

## Inputs

| Input | Source | Description |
|---|---|---|
| `query` | CLI argument (`sys.argv[1]`) or `input()` prompt | Gmail search query string (same syntax as Gmail search box) |

---

## Processing

1. Authenticate and build a Gmail API service object.
2. Call `users.messages.list` with the user-provided query plus `has:attachment` appended (e.g., `from:boss has:attachment`).
3. Request up to 3 results (`maxResults=3`); the API returns them newest-first by default.
4. For each message ID, call `users.messages.get` with `format=metadata` to retrieve headers (`From`, `Subject`, `Date`) and part metadata (to list attachment filenames).
5. Collect attachment filenames from `payload.parts` where `filename` is non-empty.

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
