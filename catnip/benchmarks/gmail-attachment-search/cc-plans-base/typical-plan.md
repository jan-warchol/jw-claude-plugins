# Plan: Gmail Attachment Search Script

## Goal

Create a Python CLI script that accepts a user-provided search query, searches Gmail for matching
emails that have attachments, and returns the 3 most recent results.

---

## Approach

Use the Gmail API via the `google-api-python-client` library with OAuth 2.0 authentication. The
script appends `has:attachment` to the user's query automatically, delegates filtering to the server
side, and fetches up to 3 results.

---

## File Structure

```
gmail_search/
├── search_gmail.py        # Main script
├── credentials.json       # OAuth client secrets (user-provided, not committed)
├── token.json             # Auto-generated after first auth (not committed)
└── requirements.txt
```

---

## Implementation Steps

### Step 1 — Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Record in `requirements.txt` and install with `pip install -r requirements.txt`.

### Step 2 — Google Cloud Setup (user prerequisite)

- Enable the Gmail API in Google Cloud Console.
- Create OAuth 2.0 credentials (Desktop application type).
- Download `credentials.json` and place it in the project directory.

### Step 3 — Authentication

- Check for a cached `token.json`; if missing or expired, launch the OAuth browser flow and save the
  new token.
- Return an authenticated Gmail API service object.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`

### Step 4 — Search Query and API Call

Build the full query:

```python
full_query = f"({user_query}) has:attachment"
```

Call `service.users().messages().list()` with `userId="me"`, `q=full_query`, and `maxResults=3`. For
each returned message ID, call `service.users().messages().get()` to retrieve headers (`From`,
`Subject`, `Date`) and attachment filenames from `payload.parts`.

### Step 5 — Output

Print a summary for each of the (up to) 3 results:

```
--- Email 1 ---
Date:        Thu, 20 Apr 2026 14:32:00 +0000
From:        sender@example.com
Subject:     Q1 Invoice
Attachments: invoice.pdf, receipt.png
```

If no results are found, print a clear message and exit.

### Step 6 — CLI Interface

Accept the search query as a command-line argument; fall back to an interactive prompt if none is
provided:

```bash
python search_gmail.py "invoice from:boss@example.com"
```

---

## Error Handling

| Scenario                        | Handling                                                     |
| ------------------------------- | ------------------------------------------------------------ |
| `credentials.json` missing      | Print setup instructions and exit                            |
| No emails match the query       | Print a friendly "no results" message and exit               |
| API / network error             | Catch `HttpError`, print the error message, and exit cleanly |
| Token expired and refresh fails | Prompt the user to re-authenticate                           |
| Email with no readable metadata | Fall back to `"(unknown)"` for missing fields                |

---

## Out of Scope

- Downloading attachment files (only filenames are reported).
- Pagination beyond the first 3 results.
- Support for multiple Gmail accounts.
