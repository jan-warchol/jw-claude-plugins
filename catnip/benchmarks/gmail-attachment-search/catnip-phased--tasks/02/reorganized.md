# Gmail Attachment Search Script

## Overview

A single-file command-line Python script that authenticates with the Gmail API, searches for emails matching a user-supplied Gmail query, and prints the 3 most recent results that contain attachments. Intended as a simple utility, not a library.

## Behavior

### Input

- The user provides a search query as a command-line argument (e.g. `python search_gmail.py "from:boss subject:report"`).
- The query follows Gmail search syntax (same as the Gmail search box).
- The script automatically appends `has:attachment` to the query so that the Gmail API handles attachment filtering server-side, avoiding the need to paginate through large result sets client-side.

### Processing

1. Execute the combined query (`<user query> has:attachment`) via `messages.list`.
2. Fetch full message metadata for each result until 3 are collected or results are exhausted.
3. Print results newest first.

### Output

Print to stdout, one block per message:

```
Date:    Mon, 12 May 2025 09:14:03 +0000
From:    boss@example.com
Subject: Q2 Report
Attachments:
  - report.pdf (application/pdf)
  - data.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
```

Each block is separated by a blank line. No machine-readable format is produced.

### Edge Cases

- Fewer than 3 matching messages: print however many exist.
- No matches: print `No emails with attachments found for query: "<query>"` and exit 0.
- Network or API errors: print the error message to stderr and exit with code 1.

## Setup & Authentication

- OAuth 2.0 via `google-auth-oauthlib`; required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Requires `credentials.json` (OAuth client credentials from Google Cloud Console) in the working directory. If missing, the script prints a descriptive setup hint and exits with code 1.
- On first run, opens a browser for user authorization and writes `token.json` for reuse. Token refresh is handled automatically; the user is not re-prompted unless the token is revoked.
- Assumes the user has already created a Google Cloud project, enabled the Gmail API, and downloaded `credentials.json`. The script does not walk through this setup.
- Assumes a browser is available for the first-run OAuth flow (or the user can copy-paste the URL manually).
- Assumes a personal Gmail account (not a Workspace account with admin-restricted API access).

## Design Notes

**Gmail API vs. IMAP:** The Gmail API is preferred because it exposes rich MIME part metadata without downloading full message bodies, and it supports Gmail's full search syntax. IMAP would require storing an app password and lacks server-side query power.

**Server-side attachment filter:** Appending `has:attachment` to the query avoids fetching pages of results that must be inspected client-side, keeping the implementation simple and fast for large mailboxes. The script fetches only the first API page (up to 100 results), which is sufficient given the server-side filter.

**Dependencies:** `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.

## Non-Goals

- Downloading or saving attachment contents.
- Modifying, labeling, or deleting emails.
- Sending emails.
- Supporting multiple Gmail accounts simultaneously.
- Structured output formats (JSON, CSV).
- Headless / service-account authentication.
