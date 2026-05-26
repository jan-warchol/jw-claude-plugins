# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and prints the 3 most recent emails matching that query that contain at least one attachment. Results are written to stdout; the script exits with code 0 on success and non-zero on error.

## Inputs

- **Query string**: provided as a command-line argument (e.g., `python search_gmail.py "invoice from:boss@example.com"`). The argument is passed directly to the Gmail search API; standard Gmail search operators are supported.

## Output

For each of the up to 3 matching emails (most recent first), print a block:

```
Subject: <value or "(no subject)">
From:    <value or "(unknown)">
Date:    <raw RFC 2822 header value>
Attachments: file1.pdf, file2.png
---
```

If a header is absent, substitute the parenthetical fallback. If fewer than 3 emails match, print only those that do.

## Authentication

- Use the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- OAuth2 credentials stored in `credentials.json` (downloaded from Google Cloud Console).
- Access token cached in `token.json` alongside the script; refreshed automatically when expired.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`
- On first run, a browser window opens for the user to grant consent; subsequent runs use the cached token silently.
- `token.json` contains sensitive refresh tokens; users should restrict its file permissions (`chmod 600`).

## Search logic

1. Append `has:attachment` to the user's query to filter for emails with attachments.
2. Call `users.messages.list` with `maxResults=3` and the combined query. Gmail returns results newest-first by default; no explicit sort parameter is needed.
3. For each returned message ID, call `users.messages.get` with `format=metadata` and metadata headers `["Subject", "From", "Date"]`.
4. Extract attachment filenames by walking `payload.parts` recursively, collecting entries where `part.filename` is non-empty. Recursion is necessary because MIME multipart messages can have nested parts.

## Error handling

- If `credentials.json` is missing, print a setup instruction (pointing to Google Cloud Console) and exit with code 1.
- If no messages are found, print "No matching emails with attachments found." and exit with code 0.
- Surface Gmail API HTTP errors with their status code and message; exit with code 1.
- If the OAuth consent flow is cancelled, print an appropriate message and exit with code 1.

## Design choices and trade-offs

- **Gmail API over IMAP**: the Gmail API supports the full Gmail search syntax (labels, operators) and handles OAuth natively; IMAP would require app passwords and offers weaker search.
- **`format=metadata` over `format=full`**: fetching only headers is faster and avoids downloading body content, which is unnecessary for this task.
- **`maxResults=3` in the list call**: avoids fetching more message IDs than needed; relies on Gmail's default newest-first ordering rather than a client-side sort.

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Files

| File | Purpose |
|---|---|
| `search_gmail.py` | Main script |
| `credentials.json` | OAuth2 client secrets (user-provided) |
| `token.json` | Cached access/refresh token (auto-created) |

## Assumptions and risks

- Assumes the Gmail API is enabled in the user's Google Cloud project and the OAuth client is of type "Desktop app".
- `maxResults=3` returns at most 3 results; Gmail may return fewer if the mailbox has fewer matches — this is handled gracefully.
- Inline images embedded as MIME parts with filenames will appear in the attachment list; this is acceptable given the script's simplicity goal.

## Non-goals

- Downloading attachment content
- Pagination beyond the first 3 results
- GUI or interactive prompts beyond the CLI argument
- Filtering by attachment type or size
