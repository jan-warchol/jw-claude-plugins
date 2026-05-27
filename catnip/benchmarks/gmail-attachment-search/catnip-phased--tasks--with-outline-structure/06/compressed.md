# Gmail Attachment Search — Spec

## Objective

CLI Python script: takes a search query, queries Gmail via the API, prints the 3 most recent matching emails that have attachments. Target user: developer/power user wanting terminal-level access to Gmail without a browser.

---

## Requirements

### Behaviour
- CLI argument: search query string (e.g. `python search.py "invoice from:boss@example.com"`).
- Authenticate via OAuth 2.0; credentials stored locally.
- Print up to 3 most-recent attachment-bearing matches, ordered newest-first.
- Per result: subject, sender, date, attachment filenames.

### Edge cases
| Situation | Behaviour |
|---|---|
| < 3 results | Print found results + "Only N result(s) found." |
| 0 results | "No matching emails with attachments found." — exit 0 |
| API quota exceeded | Print API error — exit 1 |
| Missing `credentials.json` | Print setup instructions — exit 1 |
| `token.json` refresh fails | Delete stale token, re-prompt auth |
| Any other error | Exit non-zero |

### Constraints
- Read-only: no modifying, sending, or deleting emails.
- No plaintext credential storage beyond what the OAuth flow writes.

---

## Solution

### Setup and dependencies

**One-time prerequisite:** Create a Google Cloud project, enable the Gmail API, download `credentials.json` (OAuth 2.0 desktop client) into the script directory. Missing file → print setup hint, exit non-zero.

**Libraries:** `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
(`pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`)

### Authentication

OAuth 2.0 desktop flow, scope `https://www.googleapis.com/auth/gmail.readonly`. First run opens a browser; token saved to `token.json`. Subsequent runs load and auto-refresh; on refresh failure, delete token and re-auth.

### Search and filtering

1. Append `has:attachment` to the query if absent.
2. `users.messages.list` with `q=<query>` and `maxResults=20` (results are newest-first by default).
3. For each candidate, fetch `format=metadata` (headers: `Subject`, `From`, `Date`; plus parts). Collect until 3 attachment-bearing results found or candidates exhausted.
4. Attachment check: recursively walk `payload.parts` for any part with a non-empty `filename`.
5. If 20 candidates aren't enough, follow `nextPageToken` — cap at 3 pages.

### Output

```
1. Subject: Re: Q1 Invoice
   From:    boss@example.com
   Date:    Wed, 14 May 2025 10:32:00 -0700
   Files:   invoice_q1.pdf
```

---

## Alternative solutions considered

| Option | Why not chosen |
|---|---|
| `imaplib` | Requires app password; Google is deprecating IMAP password auth |
| `simplegmail` | Thin wrapper over the same API; extra dependency without benefit |
| Service account auth | Requires Google Workspace domain; not usable for personal Gmail |

---

## Out of scope

- Downloading attachments.
- Pagination beyond 3 pages.
- Multiple simultaneous accounts.
- GUI / web interface.
- Tests / CI.

---

## Uncertainty

- **Nested MIME trees**: Recursive part-walking handles nesting, but depth behavior is unverified against real data.
- **`has:attachment` vs. inline images**: Gmail may count `Content-Disposition: inline` images; spec counts only `filename`-bearing parts. Minor divergence is acceptable.
- **Quota**: Daily API quota applies; the 3-page cap keeps per-run usage low, and the script surfaces quota errors clearly.
