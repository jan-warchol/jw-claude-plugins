# Gmail Attachment Search — Spec

## Overview

A command-line Python script that accepts a Gmail search query from the user, searches the authenticated user's Gmail inbox, and prints the 3 most recent matching emails that contain at least one attachment.

## Authentication

- Uses the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- Requires a `credentials.json` file downloaded from Google Cloud Console (OAuth 2.0 client credentials).
- On first run, opens a browser for the user to authorize access; stores the resulting token in `token.json` for subsequent runs.
- Requested OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Input

The search query is supplied as a command-line argument:

```
python search_gmail.py "from:boss@example.com invoice"
```

The script appends `has:attachment` to the user's query before sending it to the API, so the API-level search handles attachment filtering.

## Processing

1. Build and authorize a Gmail API service object.
2. Call `users.messages.list` with the combined query (`<user_query> has:attachment`), requesting up to 3 results ordered by recency (the API returns newest first by default).
3. For each returned message ID, call `users.messages.get` with `format=metadata` to retrieve headers (Subject, From, Date) and the `parts` payload to enumerate attachment filenames.
4. Collect at most 3 messages.

## Output

Print a human-readable summary for each of the (up to) 3 messages:

```
1. Subject: Q2 Invoice
   From:    boss@example.com
   Date:    Mon, 20 May 2026 09:14:32 +0000
   Attachments: invoice_q2.pdf, terms.docx

2. ...
```

If no matching emails are found, print a clear message: `No matching emails with attachments found.`

## Error Handling

- Missing `credentials.json`: print an actionable error explaining how to obtain it from Google Cloud Console and exit with code 1.
- API errors (network failure, quota exceeded): surface the error message and exit with code 1.
- Zero results: print the "no results" message and exit with code 0.

## Dependencies

| Package | Purpose |
|---|---|
| `google-api-python-client` | Gmail REST API client |
| `google-auth-oauthlib` | OAuth 2.0 browser flow |
| `google-auth-httplib2` | HTTP transport for auth |

Install via: `pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

## File Layout

```
search_gmail.py      # main script
credentials.json     # OAuth client secret (user-provided, not committed)
token.json           # cached OAuth token (auto-generated, not committed)
```

## Out of Scope

- Downloading or saving attachment contents.
- Pagination beyond the first 3 results.
- Support for multiple Gmail accounts simultaneously.
- A graphical or web interface.
