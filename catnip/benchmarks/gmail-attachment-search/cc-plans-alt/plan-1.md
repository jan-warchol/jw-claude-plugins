# Plan: Gmail Attachment Search Script

## Goal

A Python CLI script that accepts a search query, searches the user's Gmail inbox for matching emails
that have attachments, and prints details of the last 3 matches.

## Approach

Use the official **Google Gmail API** via `google-api-python-client` and `google-auth-oauthlib`.
This requires a one-time OAuth2 setup with credentials downloaded from Google Cloud Console.

## Steps

### 1. Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Install via: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### 2. Authentication

- Load `credentials.json` (downloaded from Google Cloud Console).
- On first run, open a browser for OAuth2 consent; cache the token in `token.json`.
- On subsequent runs, load the cached token (refresh automatically if expired).
- Scope required: `https://www.googleapis.com/auth/gmail.readonly`

### 3. Search logic

- Append `has:attachment` to whatever query the user passes, so the final query is e.g.
  `from:boss@example.com has:attachment`.
- Call `gmail.users().messages().list()` with `maxResults=3` and sort order newest-first (default
  Gmail API order).
- Retrieve full message details for each result via `gmail.users().messages().get()`.

### 4. Extract and display

For each of the (up to) 3 messages, print:

- Message ID
- Date
- From
- Subject
- List of attachment filenames and MIME types

### 5. Script interface

```
python search_gmail.py "your search query"
```

## File layout

```
plans/
  plan-1.md          ← this file
  search_gmail.py    ← implementation
```

## Error handling

- Missing `credentials.json` → clear message pointing to Google Cloud Console.
- No results found → friendly "no emails found" message.
- Fewer than 3 results → print however many exist.
