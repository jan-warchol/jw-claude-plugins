# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, searches for emails matching a user-supplied query string, filters for messages that have attachments, and prints the last 3 matching results.

## Usage

```
python gmail_search.py "<query>"
```

Example:
```
python gmail_search.py "from:boss@example.com invoice"
```

## Behavior

1. The script accepts one positional argument: a Gmail search query string (same syntax as the Gmail search bar).
2. It authenticates with the Gmail API using OAuth 2.0. On first run it opens a browser for authorization and saves a `token.json` credential file for subsequent runs.
3. It searches the user's inbox using the provided query, requesting results in reverse-chronological order (newest first).
4. From the results, it identifies emails that contain at least one attachment (non-inline file part with a filename).
5. It collects the first 3 such emails (i.e. the 3 most recent matches with attachments).
6. For each of those emails it prints:
   - Date sent
   - Sender (`From` header)
   - Subject
   - List of attachment filenames and their MIME types

## Authentication

- Uses Google's OAuth 2.0 for installed applications.
- Requires a `credentials.json` file (downloaded from Google Cloud Console) in the working directory.
- Scopes: `https://www.googleapis.com/auth/gmail.readonly`
- Token cached in `token.json` in the working directory; refreshed automatically when expired.

## Output Format

Plain text to stdout, one block per email:

```
--- Email 1 ---
Date:    Thu, 22 May 2025 14:30:00 +0000
From:    boss@example.com
Subject: Q2 Invoice
Attachments:
  - invoice_q2.pdf  (application/pdf)
  - receipt.png     (image/png)

--- Email 2 ---
...
```

If fewer than 3 matching emails with attachments are found, print however many exist and show a note: `(Found N email(s) with attachments matching your query.)`

If no matching emails are found, print: `No emails with attachments found for query: "<query>"`

## Error Handling

- Missing `credentials.json`: print a clear message explaining the file is required and how to obtain it, then exit with code 1.
- Gmail API errors (quota exceeded, network failure): print the error message and exit with code 1.
- Invalid or empty query string: print usage hint and exit with code 1.

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

All installable via pip:
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Files

| File | Purpose |
|---|---|
| `gmail_search.py` | Main script |
| `credentials.json` | OAuth client secrets (user-provided, not committed) |
| `token.json` | Cached access/refresh token (auto-generated, not committed) |

## Out of Scope

- Downloading attachment content.
- Support for multiple Gmail accounts.
- GUI or web interface.
- Pagination beyond what is needed to find 3 results.
