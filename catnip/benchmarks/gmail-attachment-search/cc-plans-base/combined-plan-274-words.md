# Plan: Gmail Attachment Search Script

## Goal

Python CLI script that accepts a search query, searches Gmail for matching emails with attachments,
and returns the 3 most recent results. Uses `google-api-python-client` with OAuth 2.0.

## File Structure

```
gmail_search/
├── search_gmail.py
├── credentials.json    # OAuth client secrets (add to .gitignore)
├── token.json          # Auto-generated after first auth (add to .gitignore)
└── requirements.txt
```

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Google Cloud Setup (one-time)

1. Enable the Gmail API in Google Cloud Console.
2. Create OAuth 2.0 credentials (Desktop App type).
3. Download `credentials.json` to the project directory.

## Authentication

Load `credentials.json`; check for a cached `token.json` — if missing or expired, launch the OAuth
browser flow and save the new token. The library handles token refresh automatically. Scope:
`https://www.googleapis.com/auth/gmail.readonly` (least privilege).

## Search and API Call

Build the query:

```python
full_query = f"({user_query}) has:attachment"
```

Call `service.users().messages().list()` with `userId="me"`, `q=full_query`, `maxResults=3`. Gmail
returns results newest-first, so no pagination is needed. For each message ID, call
`messages().get(format="full")` to retrieve `From`, `Subject`, `Date` headers and walk
`payload.parts` for non-empty `filename` fields.

## Output

```
--- Email 1 ---
Date:        Thu, 20 Apr 2026 14:32:00 +0000
From:        sender@example.com
Subject:     Q1 Invoice
Attachments: invoice.pdf, receipt.png
```

Print a clear message and exit if no results are found.

## CLI Interface

Accept the query via `argparse`; fall back to an interactive prompt if no argument is given:

```bash
python search_gmail.py "invoice from:boss@example.com"
```

## Error Handling

| Scenario                     | Handling                                             |
| ---------------------------- | ---------------------------------------------------- |
| `credentials.json` missing   | Print setup instructions and exit                    |
| No matching emails           | Print a friendly message and exit                    |
| API / network error          | Catch `HttpError`, print the error, and exit cleanly |
| Token expired, refresh fails | Delete `token.json` and prompt re-authentication     |
| Missing email headers        | Fall back to `"(unknown)"` for missing fields        |

## Out of Scope

- Downloading attachment files (filenames only are reported).
- Pagination beyond 3 results.
- Multiple Gmail accounts.
- Sending, deleting, or modifying emails.
