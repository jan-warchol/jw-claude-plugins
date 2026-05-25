# Plan: Gmail Attachment Search Script

## Goal

A Python CLI script that accepts a search query, searches Gmail for matching emails that have
attachments, and returns the last 3 results with their details.

## Approach

Use the Gmail API via `google-api-python-client` and `google-auth-oauthlib` with OAuth2
authentication.

## Steps

### 1. Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Install via: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### 2. Authentication

- Load `credentials.json` (downloaded from Google Cloud Console).
- On first run, open a browser for OAuth2 consent; cache the token in `token.json`.
- On subsequent runs, load the cached token; the Google client library handles refresh automatically
  if expired.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`

### 3. Search

- Accept the query as a command-line argument (fall back to interactive input if omitted).
- Append `has:attachment` to the user's query so Gmail filters server-side.
- Call `users.messages.list` with the combined query and `maxResults=3`; results are newest-first by
  default.

### 4. Detail Fetching

- For each message ID returned, call `users.messages.get` with `format=metadata` and
  `metadataHeaders=["Subject","From","Date"]`.
- Walk `payload.parts` to collect attachment filenames and MIME types (any part where `filename` is
  non-empty).

### 5. Output

- Print a numbered list for each email:
  - Date, From, Subject
  - List of attachment filenames

## Key Design Decisions

- `has:attachment` is appended automatically; users don't need to type it.
- `format=metadata` keeps API responses small — the full message body is not needed.
- `maxResults=3` is passed directly to the API instead of fetching more and slicing locally.
- Token refresh is handled automatically by the Google client library.

## File Layout

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (user-supplied, not committed)
token.json                   # auto-created after first auth
```

## Usage

```
python gmail_attachment_search.py "invoice from:boss@company.com"
```

## Error Handling

- Missing `credentials.json` → clear message directing user to Google Cloud Console.
- No results found → friendly "no emails found" message.
- Fewer than 3 results → print however many exist.
