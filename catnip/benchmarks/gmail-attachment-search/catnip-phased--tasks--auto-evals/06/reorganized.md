# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, runs a user-supplied search query, and prints the three most recent matching emails that contain at least one attachment. "Attachment" means any message part with a non-empty `filename` field in the MIME tree — this includes inline images with a filename; purely inline content without a filename is excluded.

## Authentication

- Uses the Gmail API via `google-auth` and `google-api-python-client`.
- OAuth 2.0 credentials are read from a `credentials.json` file (downloaded from Google Cloud Console). The credentials must be for an **installed application** — a service-account credential will not work with the readonly user scope.
- On first run, opens a browser for user consent; stores the resulting token in `token.json` for subsequent runs. The library handles token refresh automatically.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Does not support headless/server environments (OAuth flow requires a browser).

## Interface

### Input

| Argument | Flag | Notes |
|---|---|---|
| Search query | `--query` / `-q` | Passed directly to the Gmail API `q` parameter |

```
python gmail_search.py --query "invoice from:billing@example.com"
```

### Output

For each of the (up to 3) matching emails, print:

```
--- Email 1 ---
Date:    <date>
From:    <sender>
Subject: <subject>
Attachments:
  - filename.pdf (application/pdf, 45 KB)
  - photo.jpg (image/jpeg, 200 KB)
```

File size is derived from the `size` field of the message part; displayed in KB (rounded).

## Core Logic

1. Authenticate and build the Gmail API service.
2. Call `users.messages.list` with the user query; request up to 100 results (newest first).
3. For each message (in order), fetch the full message via `users.messages.get` with `format=full`.
4. Recursively walk the MIME part tree; collect parts where `filename` is non-empty.
5. If at least one such part exists, the email qualifies.
6. Stop once 3 qualifying emails have been found, or all retrieved results are exhausted.

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to the Google Cloud Console setup guide, then exit.
- No matching emails found: print `"No emails found matching query: <query>"`.
- Fewer than 3 matching emails with attachments: print however many were found.
- API errors: surface the error message and exit with a non-zero code.

## Design Decisions

**Gmail API over IMAP.** The Gmail API exposes the full MIME structure and attachment metadata without downloading bodies, and its query syntax (`q`) is identical to the Gmail search bar — more powerful and familiar than IMAP `SEARCH`. IMAP would require parsing raw MIME and re-implementing Gmail's query semantics.

**`format=full` without downloading attachment data.** Fetching `format=full` returns the complete MIME tree including part metadata (filename, MIME type, size) but not the attachment bytes themselves. This is sufficient to detect and describe attachments cheaply. The script never downloads attachment content.

**100-result cap, no pagination.** Fetching the first page (max 100) is a deliberate simplicity trade-off: the script is a quick lookup tool, not a bulk processor. If fewer than 3 of the first 100 results have attachments, the script reports what it found. Pagination and downloading/saving attachment files are explicitly out of scope.

**Single account only.** The script supports one authenticated Gmail account at a time, matching the scope of a personal utility script.

## Risks

- Gmail API quotas (default 1 billion units/day, ~5 units per `messages.get`) are unlikely to be an issue for this use case.

## Setup

**Dependencies** (`requirements.txt`):
```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

**Files:**
```
gmail_search.py       # main script
credentials.json      # OAuth client secret (user-provided, not committed)
token.json            # stored OAuth token (auto-generated, not committed)
requirements.txt      # pip dependencies
```
