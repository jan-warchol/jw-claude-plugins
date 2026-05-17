# Plan: Gmail Attachment Search Script

## Goal

A Python CLI script that accepts a search query from the user, searches Gmail for matching emails,
and returns the 3 most recent results that contain attachments.

---

## Approach

Use the Gmail API via the `google-api-python-client` library with OAuth 2.0 for authentication. The
script will:

1. Authenticate with Gmail using OAuth 2.0 credentials stored locally.
2. Accept a search query string from the user (CLI argument or `input()`).
3. Search Gmail using the query, appending `has:attachment` to ensure only emails with attachments
   are returned.
4. Fetch message details for the top 3 results.
5. Print a summary of each email (date, sender, subject, attachment filenames).

---

## File Structure

```
gmail_search/
├── main.py            # Entry point: CLI arg parsing, orchestration
├── auth.py            # OAuth 2.0 flow, token refresh, service object
├── search.py          # Gmail search and message detail fetching
└── credentials.json   # Downloaded from Google Cloud Console (user-provided)
```

---

## Implementation Steps

### Step 1 — Dependencies

Install required packages:

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Add a `requirements.txt` listing these three packages.

### Step 2 — Google Cloud Setup (user prerequisite)

- Enable the Gmail API in Google Cloud Console.
- Create OAuth 2.0 credentials (Desktop application type).
- Download `credentials.json` and place it in the project directory.

### Step 3 — `auth.py`

- Load `credentials.json`.
- Check for a cached `token.json`; refresh or run the OAuth flow if missing or expired.
- Return an authenticated `googleapiclient.discovery.Resource` (Gmail service object).
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`

### Step 4 — `search.py`

**`search_messages(service, query, max_results=3)`**

- Build the final query: `f"{query} has:attachment"`.
- Call `service.users().messages().list(userId="me", q=query, maxResults=max_results)`.
- Return the list of message ID/thread ID dicts (up to 3).

**`get_message_details(service, msg_id)`**

- Call `service.users().messages().get(userId="me", id=msg_id, format="full")`.
- Extract from headers: `Date`, `From`, `Subject`.
- Walk `payload.parts` to find parts where `filename` is non-empty — collect attachment filenames.
- Return a dict: `{date, sender, subject, attachments: [filename, ...]}`.

### Step 5 — `main.py`

- Parse CLI argument: `python main.py "invoice from:boss@example.com"` or prompt if no arg given.
- Call `auth.get_service()` to authenticate.
- Call `search.search_messages(service, query)`.
- If no results, print a friendly message and exit.
- For each message ID, call `search.get_message_details(service, msg_id)` and print a formatted
  summary.

**Output format per email:**

```
--- Email 1 ---
Date:        Thu, 20 Apr 2026 14:32:00 +0000
From:        boss@example.com
Subject:     Q1 Invoice
Attachments: invoice_q1.pdf, receipt.png
```

---

## Edge Cases

| Scenario                      | Handling                                                           |
| ----------------------------- | ------------------------------------------------------------------ |
| Fewer than 3 matching emails  | Print however many are found; no error                             |
| Email has no readable headers | Fall back to `"(unknown)"` for missing fields                      |
| `credentials.json` missing    | Exit with a clear error message pointing to setup instructions     |
| Token expired                 | `google-auth` handles silent refresh automatically                 |
| Network error                 | Let the exception propagate with its message; no silent swallowing |

---

## Out of Scope

- Downloading attachment files (only filenames are reported).
- Pagination beyond the first 3 results.
- Support for multiple Gmail accounts.
- Sending, deleting, or modifying emails.
