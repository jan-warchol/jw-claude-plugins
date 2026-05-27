# Gmail Attachment Search Script — Spec

## Objective

Python CLI script that accepts a Gmail search query and returns the 3 most recent matching emails that have attachments (subject, sender, date, filenames).

---

## Requirements

### Must do
- Accept query as a CLI argument, or prompt interactively if omitted.
- Authenticate via Gmail API OAuth 2.0.
- Return up to 3 most recent matching messages with attachments (most recent first); show fewer if fewer exist.
- Per result: display subject, sender, date, attachment filename(s).

### Must not do
- Download or save attachments.
- Modify, delete, or send emails.
- Store credentials in plain text.

---

## Solution

### Setup and authentication

Requires a Google Cloud project with Gmail API enabled and `credentials.json` (OAuth client secret) in CWD; if absent, exit with setup instructions. On first run, perform the OAuth 2.0 browser flow and cache the token in `token.json` (CWD); subsequent runs reuse it, auto-refreshing on expiry.

Scope: `https://www.googleapis.com/auth/gmail.readonly`  
Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`. Python 3.8+.

### Search and retrieval

Call `users.messages.list` with the query, appending `has:attachment` if not already present. Request `maxResults=10` as a buffer for API over-matching. For each returned message ID, call `users.messages.get` with `format=metadata` (avoids fetching body payloads); retrieve `Subject`, `From`, `Date` headers and scan `parts` for entries with a non-empty `filename` and `attachmentId`. Take the first 3 with confirmed attachments.

### Output and error handling

```
1. Subject: Q3 report
   From: alice@example.com
   Date: Mon, 26 May 2026 10:00:00 +0000
   Attachments: q3_report.pdf, budget.xlsx
```

- **Missing/malformed `credentials.json`**: print setup instructions, exit non-zero.
- **Auth / token failure**: print error, exit. No silent retries.
- **API error**: surface message, exit.
- **Zero results**: print "No matching emails with attachments found.", exit 0.

---

## Alternative solutions considered

- **`imaplib` + IMAP**: requires app passwords, slower search, no structured attachment metadata.
- **`simplegmail`**: friendlier wrapper but extra dependency with no benefit for a simple script.

---

## Out of scope

- Downloading/saving attachments; modifying emails; multiple accounts; pagination; GUI; tests; pip packaging; quota management.

---

## Uncertainty

- **Attachment definition**: `has:attachment` matches inline images too. Need to validate whether filtering on `attachmentId` (vs. `Content-Disposition: attachment`) correctly excludes inline parts.
- **File path configurability**: `credentials.json` and `token.json` default to CWD; no CLI/env-var override specified.
- **Output format**: plain text assumed; JSON not requested.
