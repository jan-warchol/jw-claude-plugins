# Gmail Attachment Search Script

## Overview

CLI Python script that authenticates with Gmail via OAuth2, takes a search query, and prints the 3 most recent matching emails that have attachments. Exits 0 on success, non-zero on error.

## Inputs

- **Query string**: CLI argument passed directly to the Gmail API (e.g., `python search_gmail.py "invoice from:boss@example.com"`). Standard Gmail search operators are supported.

## Output

Up to 3 results, newest first:

```
Subject: <value or "(no subject)">
From:    <value or "(unknown)">
Date:    <raw RFC 2822 header value>
Attachments: file1.pdf, file2.png
---
```

Missing headers use the parenthetical fallback. Fewer than 3 matches prints fewer blocks.

## Authentication

- Libraries: `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`
- `credentials.json`: OAuth2 client secrets (user-provided from Google Cloud Console).
- `token.json`: cached access/refresh token (auto-created); refresh on expiry. Restrict permissions with `chmod 600`.
- First run opens a browser for consent; subsequent runs are silent.

## Search logic

1. Append `has:attachment` to the user's query.
2. `users.messages.list` with `maxResults=3` — Gmail returns newest-first by default.
3. `users.messages.get` with `format=metadata`, headers `["Subject", "From", "Date"]` per message.
4. Walk `payload.parts` recursively; collect entries where `part.filename` is non-empty.

## Error handling

| Condition | Output | Exit code |
|---|---|---|
| `credentials.json` missing | Setup instruction + Google Cloud Console link | 1 |
| No matching messages | "No matching emails with attachments found." | 0 |
| Gmail API HTTP error | Status code + error message | 1 |
| OAuth consent cancelled | Message | 1 |

## Design choices

- **Gmail API over IMAP**: full Gmail search syntax, native OAuth; IMAP requires app passwords and lacks label/operator support.
- **`format=metadata`**: headers-only fetch avoids downloading bodies.
- **`maxResults=3`**: no over-fetching; relies on Gmail's native newest-first ordering.

## Assumptions and risks

- Gmail API must be enabled in the user's Google Cloud project; OAuth client type must be "Desktop app".
- Inline images with filenames appear as attachments — acceptable for a simple script.

## Non-goals

- Downloading attachment content
- Pagination beyond 3 results
- GUI or interactive prompts
- Filtering by attachment type or size
