# Gmail Attachment Search — Spec

## Overview

A command-line Python script that accepts a Gmail search query from the user, searches their inbox, and prints details of the last 3 matching emails that contain attachments.

## Usage

```
python search_attachments.py "<query>"
```

Example:

```
python search_attachments.py "from:boss@company.com invoices"
```

## Behaviour

1. Accept a single positional argument: the Gmail search query string.
2. Search Gmail using that query, appending `has:attachment` so only emails with attachments are returned.
3. Retrieve up to the 3 most recent matching threads/messages (newest first).
4. For each matching email, print:
   - Date received
   - Sender (`From` header)
   - Subject
   - Names and MIME types of all attachments
5. If fewer than 3 matches exist, print however many are found.
6. If no matches exist, print a clear "no results" message and exit with code 0.

## Authentication

- Use the Gmail API via `google-auth` + `google-api-python-client`.
- OAuth 2.0 credentials are read from `credentials.json` in the working directory (downloaded from Google Cloud Console).
- On first run, open a browser for the OAuth consent flow and cache the token in `token.json`.
- On subsequent runs, load the cached token and refresh it automatically if expired.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Output Format

```
Found 3 email(s) with attachments:

1. Date:    Thu, 14 May 2026 09:22:11 -0400
   From:    boss@company.com
   Subject: Q1 Invoice
   Attachments:
     - invoice_q1.pdf (application/pdf)

2. Date:    Mon, 11 May 2026 14:05:33 -0400
   From:    billing@vendor.com
   Subject: Your receipt
   Attachments:
     - receipt.pdf (application/pdf)
     - logo.png (image/png)

3. ...
```

## Error Handling

| Condition | Behaviour |
|---|---|
| `credentials.json` missing | Print actionable error message with setup instructions; exit code 1 |
| OAuth flow cancelled by user | Print error; exit code 1 |
| Gmail API error (network, quota) | Print the API error message; exit code 1 |
| No query argument provided | Print usage hint; exit code 2 |

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

All installable via:

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Files

| File | Purpose |
|---|---|
| `search_attachments.py` | Main script |
| `credentials.json` | OAuth client secrets (user-provided, not committed) |
| `token.json` | Cached OAuth token (auto-generated, not committed) |

## Out of Scope

- Downloading attachment content
- Pagination beyond the 3 most recent results
- Sending or modifying emails
- Support for multiple Gmail accounts
