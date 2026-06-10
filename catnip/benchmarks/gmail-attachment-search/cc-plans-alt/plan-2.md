# Plan: Gmail Attachment Search Script

## Goal

A Python CLI script that accepts a Gmail search query and returns the last 3 matching emails that
contain attachments.

## Approach

Use the Gmail API via the `google-api-python-client` library. The script will:

1. Authenticate with OAuth2 using a `credentials.json` file and cache the token in `token.json`.
2. Accept a search query from the user (command-line argument or interactive prompt).
3. Call `users.messages.list` with the query `has:attachment <user_query>` to pre-filter on the
   server side — this is more efficient than fetching all messages and filtering locally.
4. Fetch the last 3 matching message IDs (the API returns newest-first by default).
5. For each message, call `users.messages.get` with `format=metadata` to retrieve headers (Subject,
   From, Date) and the `parts` structure to confirm and list attachments.
6. Print a summary of each matching email.

## Key Design Decisions

- **Pre-filter with `has:attachment`**: Combining the user query with `has:attachment` lets Gmail do
  the heavy lifting server-side instead of fetching arbitrary pages and filtering locally.
- **`format=metadata`**: Requesting only metadata (headers + part names) keeps responses small — we
  don't need the full message body.
- **Newest-first**: Gmail's `messages.list` returns results newest-first by default, so taking the
  first 3 results gives the most recent matches without extra sorting.
- **Minimal dependencies**: Only `google-api-python-client` and `google-auth-oauthlib`.

## File Layout

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth2 client credentials (user-provided, not committed)
token.json                   # cached OAuth2 token (auto-created on first run)
```

## Steps

1. Parse the search query from `sys.argv[1]` (fall back to interactive input if omitted).
2. Build the Gmail service via OAuth2 (scope: `gmail.readonly`).
3. Call `messages.list` with `q=f"has:attachment {query}"` and `maxResults=3`.
4. For each returned message ID, call `messages.get` with `format=metadata` and
   `metadataHeaders=["Subject","From","Date"]`.
5. Walk the `payload.parts` tree to collect attachment filenames and MIME types.
6. Print the Subject, From, Date, and attachment list for each email.

## Error Handling

- No credentials file → clear error message with setup instructions.
- Zero results → friendly "no emails found" message.
- Fewer than 3 results → print however many were found.
