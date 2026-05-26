# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the 3 most recent emails matching that query that contain at least one attachment.

## Inputs

- **Query string**: provided as a command-line argument (e.g., `python search_gmail.py "invoice from:boss@example.com"`)

## Output

For each of the up to 3 matching emails (most recent first), print:

- Subject
- Sender
- Date
- List of attachment filenames

## Authentication

- Use the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- OAuth2 credentials stored in `credentials.json` (downloaded from Google Cloud Console).
- Access token cached in `token.json` alongside the script; refreshed automatically when expired.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

## Search logic

1. Append `has:attachment` to the user's query to filter for emails with attachments.
2. Call `users.messages.list` with `maxResults=3` and the combined query.
3. For each returned message ID, call `users.messages.get` with `format=metadata` and metadata headers `["Subject", "From", "Date"]`.
4. Extract attachment filenames from `payload.parts` where `part.filename` is non-empty.

## Error handling

- If `credentials.json` is missing, print a clear setup instruction and exit.
- If no messages are found, print "No matching emails with attachments found."
- Surface Gmail API errors as readable messages.

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

## Non-goals

- Downloading attachment content
- Pagination beyond the first 3 results
- GUI or interactive prompts beyond the CLI argument
