# Gmail Attachment Search Script

## Overview

A single-file command-line Python script that authenticates with the Gmail API, searches for emails matching a user-supplied Gmail query, and prints the 3 most recent results that contain attachments. Intended as a simple utility, not a library.

## Functional Requirements

### Input

- The user provides a search query as a command-line argument (e.g. `python search_gmail.py "from:boss subject:report"`).
- The query follows Gmail search syntax (same as the Gmail search box).
- The script automatically appends `has:attachment` to the query so that the Gmail API handles attachment filtering server-side, avoiding the need to paginate through large result sets client-side.

### Processing

1. Authenticate with the Gmail API using OAuth 2.0.
2. Execute the combined query (`<user query> has:attachment`) via `messages.list`.
3. Fetch full message metadata for each result until 3 are collected or results are exhausted.
4. Return the 3 most recent matching messages (newest first, as returned by the API).

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
- `credentials.json` missing: print a descriptive setup hint and exit 1.

## Authentication

- OAuth 2.0 via `google-auth-oauthlib`.
- Requires `credentials.json` (OAuth client credentials downloaded from Google Cloud Console) in the working directory.
- On first run, opens a browser for user authorization and writes `token.json` for reuse.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Token refresh is handled automatically by the library; the user is not re-prompted unless the token is revoked.

## Assumptions

- The user has already created a Google Cloud project, enabled the Gmail API, and downloaded `credentials.json`. The script does not walk through this setup.
- The script is run in an environment with a browser available for the first-run OAuth flow (or the user can copy-paste the URL manually via the `--no-browser` flag in `InstalledAppFlow`).
- The Gmail account is personal (not a Workspace account with admin-restricted API access).

## Design Choices and Trade-offs

**Gmail API vs. IMAP:** The Gmail API is preferred because it exposes rich MIME part metadata without downloading full message bodies, and it supports Gmail's full search syntax. IMAP would require storing an app password and lacks server-side query power.

**Server-side attachment filter (`has:attachment`):** Appending this to the query avoids fetching pages of results that must be inspected client-side, keeping the implementation simple and fast for large mailboxes.

**No pagination loop:** The script fetches only the first API page (up to 100 results by default, configurable with `maxResults`). Because `has:attachment` is applied server-side, the first page almost always contains enough results for the 3-message target. A full pagination loop is out of scope.

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- `google-api-python-client`

## Non-Goals

- Downloading or saving attachment contents.
- Modifying, labeling, or deleting emails.
- Sending emails.
- Supporting multiple Gmail accounts simultaneously.
- Structured output formats (JSON, CSV).
- Headless / service-account authentication.
