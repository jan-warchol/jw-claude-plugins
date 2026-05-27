# Gmail Attachment Search — Spec

## Objective

Build a small Python script that accepts a search query from the user, searches their Gmail inbox via the Gmail API, and prints the three most recent matching emails that contain at least one attachment.

The target user is a developer or power user who wants a scriptable, terminal-friendly way to locate attachment-bearing emails without opening a browser.

---

## Requirements

### Must do
- Accept a search query string as a CLI argument (e.g., `python search.py "invoice from:boss@example.com"`).
- Authenticate with Gmail using OAuth 2.0 (Google API credentials stored locally).
- Search the user's Gmail inbox using the provided query string.
- Filter results to only emails that have at least one attachment.
- Return (print) the last 3 such emails, ordered most-recent-first.
- For each result, display: subject, sender, date, and attachment filenames.

### Must not do
- Download or save attachments to disk (out of scope).
- Modify, send, or delete any emails.
- Store credentials or tokens in plaintext beyond what the Google OAuth flow writes.

---

## Solution

### Authentication
Use the `google-auth-oauthlib` + `google-api-python-client` libraries with the OAuth 2.0 desktop flow:
- On first run, open a browser for the user to grant access; store the resulting token in `token.json`.
- On subsequent runs, load the token from `token.json`, refreshing automatically if expired.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.

### Search and filtering
1. Call `users.messages.list` with the user's query string plus the implicit filter `has:attachment` appended (or combined) to pre-filter at the API level.
2. The API returns message IDs in reverse-chronological order by default.
3. Fetch full message metadata (`format=metadata`, fields: `payload.headers`, `payload.parts`) for each candidate until 3 attachment-bearing results are collected, or the result set is exhausted.
4. Confirm attachment presence by checking `payload.parts` for any part with a non-empty `filename`.

### Output
Print a numbered list to stdout:

```
1. Subject: Re: Q1 Invoice
   From:    boss@example.com
   Date:    Wed, 14 May 2025 10:32:00 -0700
   Files:   invoice_q1.pdf
```

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

All installable via `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`.

### Credentials setup (user-facing prerequisite)
The user must create a Google Cloud project, enable the Gmail API, and download `credentials.json` (OAuth 2.0 desktop client) into the same directory as the script. This is a one-time setup documented in a brief README comment at the top of the script.

---

## Alternative solutions considered

| Option | Why not chosen |
|---|---|
| `imaplib` (raw IMAP) | Requires app password or less-secure-apps toggle; Google is deprecating IMAP password auth |
| `simplegmail` (third-party wrapper) | Extra dependency with less control; thin wrapper around the same API |
| Service account auth | Requires G Suite / Google Workspace domain; not suitable for personal Gmail |

---

## Out of scope

- Downloading or saving attachment content.
- Pagination beyond what is needed to collect 3 results.
- Support for multiple Gmail accounts simultaneously.
- GUI or web interface.
- Unit tests / CI (this is a simple standalone script).

---

## Uncertainty

- **Quota limits**: The Gmail API has a daily quota. For typical one-off use this is not a concern, but repeated invocations in quick succession could hit rate limits. The script should surface a clear error if a quota error is returned.
- **Nested multipart messages**: Some emails have deeply nested `multipart/*` MIME trees. The attachment-detection logic needs to recurse into nested parts, not just check the top-level `payload.parts`. The correct depth of recursion is unclear until tested against real data.
- **`has:attachment` reliability**: Gmail's `has:attachment` query modifier should handle most cases, but inline images embedded via `Content-Disposition: inline` may or may not be counted. The spec currently counts only `filename`-bearing parts as attachments, which may diverge from what Gmail's own filter counts.
