# Gmail Attachment Search Script

## Overview

A single-file CLI Python script that searches Gmail and prints the 3 most recent emails with attachments matching a user query. Simple utility, not a library.

## Behavior

### Input

- Search query as a CLI argument (e.g. `python search_gmail.py "from:boss subject:report"`), using Gmail search syntax.
- The script appends `has:attachment` automatically for server-side filtering.

### Processing

1. Run the combined query (`<user query> has:attachment`) via `messages.list`.
2. Fetch full metadata for each result until 3 are collected or results exhausted.
3. Print newest first.

### Output

```
Date:    Mon, 12 May 2025 09:14:03 +0000
From:    boss@example.com
Subject: Q2 Report
Attachments:
  - report.pdf (application/pdf)
  - data.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
```

Blocks separated by a blank line; plain text only.

### Edge Cases

- Fewer than 3 results: print however many exist.
- No results: print `No emails with attachments found for query: "<query>"`, exit 0.
- API/network error: print to stderr, exit 1.

## Setup & Authentication

- OAuth 2.0 via `google-auth-oauthlib`; scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Requires `credentials.json` (from Google Cloud Console) in the working directory; missing file exits 1 with a setup hint.
- First run opens a browser for authorization and writes `token.json`; subsequent runs reuse it with automatic token refresh.
- Assumes: Google Cloud project created, Gmail API enabled, `credentials.json` downloaded, browser available, personal (non-Workspace) account.

## Design Notes

**Gmail API vs. IMAP:** Gmail API exposes MIME metadata without downloading bodies and supports Gmail's search syntax; IMAP requires an app password and lacks server-side search.

**Server-side filter:** `has:attachment` in the query makes client-side pagination unnecessary; fetching the first page (≤100 results) is always sufficient.

**Dependencies:** `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.

## Non-Goals

- Downloading attachment contents.
- Modifying, labeling, deleting, or sending emails.
- Multiple accounts, structured output (JSON/CSV), or service-account auth.
