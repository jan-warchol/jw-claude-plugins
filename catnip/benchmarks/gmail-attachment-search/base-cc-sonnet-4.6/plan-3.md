# Plan: Gmail Attachment Search Script

## Goal

Create a Python CLI script that accepts a user-provided search query, searches Gmail for matching emails that have attachments, and returns the 3 most recent results.

---

## Approach

Use the Gmail API via the `google-api-python-client` library with OAuth 2.0 authentication. The script will append `has:attachment` to the user's query automatically, fetch up to 3 results, and print a structured summary of each email.

---

## Prerequisites

- Python 3.8+
- A Google Cloud project with the Gmail API enabled
- OAuth 2.0 credentials downloaded as `credentials.json`
- Required packages: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

---

## File Structure

```
gmail_search/
├── credentials.json       # OAuth client secrets (user-provided, not committed)
├── token.json             # Auto-generated after first auth (not committed)
├── search_attachments.py  # Main script
└── requirements.txt
```

---

## Implementation Steps

### 1. Dependencies (`requirements.txt`)

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

### 2. OAuth Authentication

- On first run, open a browser for the OAuth consent flow and save the token to `token.json`.
- On subsequent runs, load the saved token and refresh it automatically if expired.
- Scope required: `https://www.googleapis.com/auth/gmail.readonly`

### 3. Build the Search Query

Append `has:attachment` to whatever the user provides:

```python
full_query = f"({user_query}) has:attachment"
```

### 4. Call the Gmail API

Use `users.messages.list` with:
- `q=full_query`
- `maxResults=3`

Then call `users.messages.get` for each message ID with `format='metadata'` and headers `['From', 'Subject', 'Date']` to retrieve email metadata efficiently.

### 5. Output

Print a numbered list for each of the (up to) 3 emails:

```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   ID:      <message_id>
```

If no results are found, print a clear message to the user.

### 6. CLI Interface

Accept the query as a command-line argument:

```bash
python search_attachments.py "invoice from:boss@example.com"
```

---

## Error Handling

| Scenario | Handling |
|---|---|
| `credentials.json` missing | Print a clear setup instruction and exit |
| No emails match the query | Print "No matching emails with attachments found." |
| API quota/network error | Catch `HttpError`, print the error message, and exit cleanly |
| Token expired and refresh fails | Delete `token.json` and prompt the user to re-authenticate |

---

## Security Notes

- `credentials.json` and `token.json` must never be committed to version control (add both to `.gitignore`).
- Use read-only scope (`gmail.readonly`) — the script never modifies or deletes any email.

---

## Out of Scope

- Downloading attachment files (only metadata is fetched)
- Pagination beyond the first 3 results
- Support for multiple Gmail accounts
