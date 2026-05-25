# Plan: Gmail Attachment Search Script

## Goal

Create a Python CLI script that accepts a user-provided search query, searches Gmail for matching
emails that have attachments, and returns the 3 most recent results.

---

## Prerequisites

- Python 3.8+
- A Google Cloud project with the Gmail API enabled
- OAuth 2.0 credentials downloaded as `credentials.json` (Desktop App type)

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
├── credentials.json       # OAuth client secrets (user-provided; add to .gitignore)
├── token.json             # Auto-generated after first auth (add to .gitignore)
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

### Step 2 — Google Cloud Setup (one-time manual step)

1. Enable the Gmail API in Google Cloud Console.
2. Create OAuth 2.0 credentials (Desktop App type).
3. Download `credentials.json` and place it in the project directory.

### Step 3 — Authentication

- Load `credentials.json`.
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
each returned message ID, call `service.users().messages().get(format="full")` to retrieve headers
(`From`, `Subject`, `Date`) and walk `payload.parts` for non-empty `filename` fields.

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

Accept the query via `argparse`; fall back to an interactive prompt if no argument is given:

```bash
python search_gmail.py "invoice from:boss@example.com"
```

---

## Key Design Decisions

| Decision       | Choice                              | Reason                                                         |
| -------------- | ----------------------------------- | -------------------------------------------------------------- |
| Auth library   | `google-auth-oauthlib`              | Official Google library, handles token refresh automatically   |
| API scope      | `gmail.readonly`                    | Least privilege — script never modifies or deletes emails      |
| Query strategy | Append `has:attachment` server-side | More efficient than client-side filtering                      |
| Result limit   | `maxResults=3`                      | Gmail returns newest-first; no pagination needed for 3 results |
| Output format  | Plain text summary                  | Readable without extra dependencies                            |

---

## Example Usage

```bash
python search_gmail.py "invoice 2025"
```

```
--- Email 1 ---
Date:        Thu, 10 Apr 2025 09:15:00 +0000
From:        billing@acme.com
Subject:     Invoice #1042
Attachments: invoice_1042.pdf, summary.xlsx

--- Email 2 ---
Date:        Mon, 03 Mar 2025 11:42:00 +0000
From:        finance@vendor.io
Subject:     March Invoice
Attachments: march_invoice.pdf

--- Email 3 ---
Date:        Fri, 14 Feb 2025 08:30:00 +0000
From:        accounts@supplier.net
Subject:     Invoice February 2025
Attachments: feb_invoice.pdf
```

---

## Error Handling

| Scenario                               | Handling                                                     |
| -------------------------------------- | ------------------------------------------------------------ |
| `credentials.json` missing             | Print setup instructions and exit                            |
| No emails match the query              | Print a friendly "no results" message and exit               |
| API / network error                    | Catch `HttpError`, print the error message, and exit cleanly |
| Token expired and silent refresh fails | Delete `token.json` and prompt the user to re-authenticate   |
| Email with no readable headers         | Fall back to `"(unknown)"` for missing fields                |

---

## Out of Scope

- Downloading attachment files (only filenames are reported).
- Pagination beyond the first 3 results.
- Support for multiple Gmail accounts.
- Sending, deleting, or modifying emails.
