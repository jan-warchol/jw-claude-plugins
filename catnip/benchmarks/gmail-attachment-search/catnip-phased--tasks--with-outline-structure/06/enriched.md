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
- Print a clear message when fewer than 3 (or zero) results are found rather than silently truncating.
- Exit with a non-zero status code on any error (API error, missing credentials, auth failure).

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
- If `credentials.json` is absent, print a setup hint (pointing to the Google Cloud console) and exit non-zero immediately.

### Search and filtering
1. Build the effective query by appending `has:attachment` to the user's query string if it is not already present (e.g., `"invoice from:boss@example.com has:attachment"`).
2. Call `users.messages.list` with `q=<effective_query>` and `maxResults=20`. The API returns IDs in reverse-chronological order by default.
3. Fetch full message metadata (`format=metadata`, requesting headers `Subject`, `From`, `Date` and parts) for each candidate in order until 3 attachment-bearing results are collected or all candidates are exhausted.
4. Confirm attachment presence by recursively walking `payload.parts` for any part with a non-empty `filename` field (handles nested `multipart/*` trees).
5. If 20 candidates are not enough to yield 3 results, fetch the next page using the `nextPageToken` and continue — but cap at 3 pages total to avoid unbounded API calls.

### Edge case behavior
| Situation | Behaviour |
|---|---|
| Fewer than 3 attachment emails found | Print what was found; add a note: "Only N result(s) found." |
| Zero results | Print "No matching emails with attachments found." and exit 0. |
| API quota exceeded | Print the API error message and exit 1. |
| Missing `credentials.json` | Print setup instructions and exit 1. |
| `token.json` expired and refresh fails | Delete stale token, prompt re-auth. |

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
- Pagination beyond 3 pages (sufficient to collect 3 results in any realistic inbox).
- Support for multiple Gmail accounts simultaneously.
- GUI or web interface.
- Unit tests / CI (this is a simple standalone script).

---

## Uncertainty

- **Nested multipart messages**: Some emails have deeply nested `multipart/*` MIME trees. The attachment-detection logic recurses into nested parts, but the correct depth is only verified against real data. The implementation should recurse without a hard depth cap.
- **`has:attachment` vs. inline images**: Gmail's `has:attachment` may count inline images (`Content-Disposition: inline`). The spec counts only `filename`-bearing parts as "attachments", which may diverge slightly from Gmail's own definition. This is acceptable for the stated use case.
- **Quota limits**: The Gmail API has a daily quota. Repeated invocations in quick succession could hit rate limits. The 3-page cap on list calls limits per-run API usage; the script surfaces a clear error if quota is exceeded.
