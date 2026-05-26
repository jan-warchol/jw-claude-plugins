# Gmail Attachment Search — Spec

## Overview

CLI Python script: takes a Gmail search query, searches the user's entire mailbox, and prints the 3 most recent emails with attachments.

## Setup

### Authentication

- Requires `credentials.json` (OAuth 2.0 desktop-app credentials from Google Cloud Console, Gmail API enabled).
- First run opens a browser for authorization; token cached in `token.json`. Expired tokens auto-refresh; revoked access re-runs the browser flow.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.
- **Headless**: browser flow requires a desktop browser; pre-generating `token.json` elsewhere is out of scope.

### Dependencies

| Package | Purpose |
|---|---|
| `google-api-python-client` | Gmail REST API client |
| `google-auth-oauthlib` | OAuth 2.0 browser flow |
| `google-auth-httplib2` | HTTP transport for auth |

`pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

### Files

```
search_gmail.py      # main script
credentials.json     # OAuth client secret (user-provided, not committed)
token.json           # cached OAuth token (auto-generated, not committed)
```

## Behavior

### Input

Query is a CLI argument:

```
python search_gmail.py "from:boss@example.com invoice"
```

No argument → usage message, exit 1. Appends `has:attachment` to the query, delegating attachment filtering to Gmail's server-side search.

### Processing

1. Build and authorize a Gmail API service object.
2. Call `users.messages.list` with `<user_query> has:attachment`, requesting up to 3 results (API returns newest-first).
3. For each message ID, call `users.messages.get` with `format=full` (not `format=metadata`, which omits MIME parts) to get headers (Subject, From, Date) and attachment filenames.
4. Extract filenames from MIME parts where `filename` is non-empty.

### Output

```
1. Subject: Q2 Invoice
   From:    boss@example.com
   Date:    Mon, 20 May 2026 09:14:32 +0000
   Attachments: invoice_q2.pdf, terms.docx

2. ...
```

Missing headers fall back to `(unknown)`. No results → `No matching emails with attachments found.`

### Error Handling

- Missing `credentials.json`: actionable error with setup instructions, exit 1.
- Missing CLI argument: usage message, exit 1.
- API errors: surface message, exit 1.
- Zero results: exit 0.

## Design Notes

**Gmail API over IMAP**: native Gmail search syntax, OAuth handled by the library, structured responses (vs raw RFC 2822).

**Server-side filtering**: `has:attachment` in the query avoids fetching non-matching messages.

**`format=full` weight**: fetches full bodies, heavier than needed, but acceptable for only 3 results.

## Out of Scope

- Downloading or saving attachment contents.
- Pagination beyond the first 3 results.
- Multiple Gmail accounts.
- GUI or web interface.
- Headless OAuth flows.
