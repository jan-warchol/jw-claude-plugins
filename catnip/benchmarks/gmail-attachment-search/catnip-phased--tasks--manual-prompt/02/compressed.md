# Gmail Attachment Search Script — Spec

## Overview

CLI Python script that authenticates with Gmail via OAuth2, accepts a search query, and prints the three most recent matching emails that have attachments (sender, subject, date, attachment filenames).

## Usage

```
python gmail_search.py "<query>"
```

Requires `credentials.json` (Desktop app OAuth2 client from Google Cloud Console) and `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Behavior

### Authentication
- First run: open browser for OAuth2 consent, save token to `token.json`.
- Subsequent runs: load and auto-refresh `token.json`.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.
- If token is unrefreshable (revoked): delete `token.json`, prompt user to re-run.

### Input
- Single positional argument: Gmail search query (standard syntax, e.g. `"from:boss invoice"`).
- Script silently appends `has:attachment`; user need not include it.

### Processing
1. Call `users.messages.list` with `<user_query> has:attachment`, up to 10 results per page.
2. Fetch `format=full` for each result, newest first, until 3 messages with a non-inline attachment are found or results are exhausted.
3. Attachment: MIME part with non-empty `filename` and `Content-Disposition: attachment`. Inline images are excluded.
4. Stop at 3; no further pagination.

### Output
```
--- Email 1 ---
From:    alice@example.com
Subject: Q1 Invoice
Date:    Mon, 12 May 2025 09:14:03 +0000
Attachments:
  - invoice_q1.pdf (application/pdf)
  - terms.docx (application/vnd.openxmlformats...)
```
Fewer than 3 results: print what exists. Zero: print `No matching emails with attachments found.`

### Error Handling
- Missing `credentials.json`: instructional error, exit 1.
- Missing/empty query: usage hint, exit 1.
- API error: print message, exit 1.

## Design Notes

### Key Choices
**Auto-append `has:attachment`:** Offloads filtering to Gmail's server, cutting API calls. Acceptable divergence from the user-typed query given the script's explicit purpose.

**`format=full` over `format=metadata`:** Needed to read MIME parts and attachment filenames; `format=metadata` cannot reliably detect attachments.

### Assumptions and Risks
- Gmail API enabled, Desktop OAuth2 `credentials.json` already obtained.
- Browser available for initial consent flow.
- `token.json` stored in plaintext — working directory must not be publicly accessible.
- API quota (1B units/day; 5 units per `messages.get`) is not a concern for ≤10 fetches per run.

### Non-Goals
Downloading attachments · pagination beyond page 1 · multiple accounts · GUI · inline images as attachments.
