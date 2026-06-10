# Plan: Gmail Attachment Search Script

## Goal

A Python script that accepts a user-provided search query, searches Gmail for matching emails that
have attachments, and returns the last 3 results with their details.

## Approach

Use the Gmail API via Google's official Python client library with OAuth2 authentication.

## Steps

### 1. Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Install via: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### 2. Authentication

- Standard OAuth2 flow using `credentials.json` from Google Cloud Console
- Token cached in `token.json` for subsequent runs
- Scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only, minimal permissions)

### 3. Search Logic

- Accept query as a command-line argument (fall back to `input()` if not provided)
- Append `has:attachment` to the user's query so Gmail filters server-side
- Call `users.messages.list` with the combined query, requesting up to 3 results (newest first —
  Gmail returns results in reverse-chronological order by default)

### 4. Detail Fetching

- For each message ID returned, call `users.messages.get` with `format=full`
- Parse headers for: `Subject`, `From`, `Date`
- Walk MIME parts to collect attachment filenames and MIME types (any part where `filename` is
  non-empty)

### 5. Output

- Print a numbered list (1–3) with:
  - Date, From, Subject
  - List of attachment filenames

## File Layout

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (user must supply)
token.json                   # auto-created after first auth
```

## Error Handling

- Missing `credentials.json` → clear message directing user to Google Cloud Console
- No matching emails → friendly "no results" message
- Fewer than 3 results → return however many exist
