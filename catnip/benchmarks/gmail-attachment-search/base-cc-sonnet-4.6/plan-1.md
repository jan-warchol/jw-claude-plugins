# Plan: Gmail Attachment Search Script

## Goal

Create a Python script that accepts a user-provided search query, searches Gmail for matching emails, and returns the last 3 that have attachments.

---

## Approach

Use the Gmail API via the `google-api-python-client` library with OAuth 2.0 authentication. The script will:

1. Authenticate with Gmail using OAuth credentials.
2. Accept a search query string from the user (CLI argument or interactive prompt).
3. Append `has:attachment` to the query to filter for emails with attachments.
4. Fetch matching message IDs, sorted by date descending.
5. Retrieve full message details for the top 3 results.
6. Print a summary of each email (subject, sender, date, attachment names).

---

## File Structure

```
gmail_search/
├── search_gmail.py       # Main script
├── credentials.json      # OAuth client secrets (downloaded from Google Cloud Console)
├── token.json            # Auto-generated OAuth token (gitignored)
└── requirements.txt
```

---

## Step-by-Step Implementation Plan

### Step 1 – Google Cloud Setup (one-time, manual)

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Gmail API**.
3. Create **OAuth 2.0 credentials** (Desktop App type).
4. Download `credentials.json` and place it in the project directory.

### Step 2 – Dependencies (`requirements.txt`)

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Install with:
```bash
pip install -r requirements.txt
```

### Step 3 – Authentication Helper

Write a `get_gmail_service()` function that:
- Checks for a cached `token.json`.
- If missing or expired, launches the OAuth browser flow to obtain and save a new token.
- Returns an authenticated Gmail API service object.

Scopes required: `https://www.googleapis.com/auth/gmail.readonly`

### Step 4 – Search Logic

```
query = f"({user_query}) has:attachment"
```

Call `service.users().messages().list()` with:
- `userId="me"`
- `q=query`
- `maxResults=10` (fetch a small buffer in case some results need to be skipped)

This returns a list of `{id, threadId}` objects ordered newest-first by default.

### Step 5 – Fetch Message Details

For each of the top message IDs (up to the first 3):
- Call `service.users().messages().get(userId="me", id=msg_id, format="full")`.
- Extract headers: `Subject`, `From`, `Date`.
- Walk the `payload.parts` tree to find `filename` fields that are non-empty (these are attachments).
- Collect attachment names and sizes.

### Step 6 – Output

Print a structured summary for each of the 3 emails:

```
--- Email 1 ---
Date:        Mon, 21 Apr 2026 14:32:00 +0000
From:        sender@example.com
Subject:     Q1 Report
Attachments: report.pdf (245 KB), chart.png (80 KB)
```

If fewer than 3 matching emails exist, print however many are found with a note.

### Step 7 – CLI Interface

Accept the query via `argparse`:

```bash
python search_gmail.py "invoice from:billing@company.com"
```

If no argument is given, prompt interactively:

```
Enter search query: invoice from:billing@company.com
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Auth library | `google-auth-oauthlib` | Official Google library, handles token refresh |
| API scope | `gmail.readonly` | Least privilege; script only reads emails |
| Query strategy | Append `has:attachment` | Delegates filtering to Gmail server-side, more efficient than client-side filtering |
| Result limit | Fetch up to 10, display 3 | Small buffer handles edge cases without over-fetching |
| Output format | Plain text summary | Simple and readable without extra dependencies |

---

## Error Handling

- Missing `credentials.json`: print a clear setup message and exit.
- No results found: print informative message instead of crashing.
- API quota/network errors: catch `googleapiclient.errors.HttpError` and print the error.
- Emails with no attachment metadata despite `has:attachment`: skip gracefully (rare Gmail indexing edge case).

---

## Out of Scope

- Downloading attachment files (only listing names/sizes).
- Pagination beyond the first page of results (3 results don't require it).
- Support for multiple Gmail accounts.
- A GUI or web interface.
