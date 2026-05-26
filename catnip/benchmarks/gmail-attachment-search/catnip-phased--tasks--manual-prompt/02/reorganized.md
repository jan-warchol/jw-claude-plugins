# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the three most recent emails matching that query which contain at least one attachment. Each result includes the sender, subject, date, and a list of attachment filenames.

## Usage

```
python gmail_search.py "<query>"
```

Example:

```
python gmail_search.py "from:finance"
```

Requires `credentials.json` (Desktop app OAuth2 client, downloaded from Google Cloud Console) and `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` installed.

## Behavior

### Authentication
- On first run, open a browser for OAuth2 consent and save the resulting token to `token.json` in the working directory.
- On subsequent runs, load `token.json` and refresh automatically if expired.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- If the token cannot be refreshed (e.g., revoked): delete `token.json` and prompt the user to re-run for a fresh OAuth2 flow.

### Input
- A single positional CLI argument: the Gmail search query string (e.g., `"from:boss invoice"`).
- The query follows Gmail's standard search syntax and is passed through unchanged to the API.
- The script silently appends `has:attachment` before sending to the API; the user does not need to include it.

### Processing
1. Call `users.messages.list` with the augmented query (`<user_query> has:attachment`), requesting up to 10 results per page.
2. Fetch full message details (`format=full`) for each result, newest first, until 3 messages with at least one non-inline attachment are collected or results are exhausted.
3. An attachment is any MIME part where `filename` is non-empty and `Content-Disposition` is `attachment` (not `inline`). Inline images embedded in HTML emails are excluded.
4. Stop after collecting 3 such messages; do not fetch further pages.

### Output
Print to stdout:

```
--- Email 1 ---
From:    alice@example.com
Subject: Q1 Invoice
Date:    Mon, 12 May 2025 09:14:03 +0000
Attachments:
  - invoice_q1.pdf (application/pdf)
  - terms.docx (application/vnd.openxmlformats...)
```

If fewer than 3 matching emails exist, print however many there are. If none, print: `No matching emails with attachments found.`

### Error Handling
- Missing `credentials.json`: print an instructional error and exit with code 1.
- Empty or missing query argument: print usage hint and exit with code 1.
- API errors (quota exceeded, network failure): print the error message and exit with code 1.

## Design Notes

### Key Choices
**Auto-appending `has:attachment`:** Offloads attachment filtering to Gmail's server, reducing messages fetched and API calls. The query sent to Gmail differs from what the user typed, but this is acceptable given the script's explicit purpose.

**`format=full` over `format=metadata`:** Required to inspect MIME parts and identify attachment filenames. `format=metadata` would be more efficient but cannot reliably detect or name attachments.

### Assumptions and Risks
- **Assumption:** The user has a Google Cloud project with the Gmail API enabled and a Desktop OAuth2 client `credentials.json`.
- **Assumption:** A browser is available for the initial consent flow.
- **Risk:** `token.json` is stored in plaintext; the working directory should not be publicly accessible.
- **Risk:** Gmail API quota is generous (1B units/day; `messages.get` costs 5 units), so up to 10 fetches per run is well within limits.

### Non-Goals
- Downloading attachment content.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts.
- Any GUI or interactive mode.
- Treating inline images as attachments.
