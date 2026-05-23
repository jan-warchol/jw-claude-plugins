# Gmail Attachment Search Script

## Overview

CLI Python script that searches the user's entire Gmail account with a query string and returns the three most recent emails with attachments.

## Inputs

- Search query as a CLI argument (e.g., `"from:boss subject:report"`), using Gmail's standard search syntax.

## Behavior

1. Authenticate via Gmail API OAuth 2.0; cache credentials for reuse.
2. Append `has:attachment` to the user's query server-side (inline images are excluded).
3. Retrieve up to three results newest-first, using `format=metadata` to minimize quota.
4. Return all matches if fewer than three exist; print a message and exit non-zero if none.

## Output

For each email, print to stdout (plain text; blank line between entries):
- Date, sender, subject
- Attachment filenames

## Authentication

- Loads `credentials.json` from the working directory; caches token in `token.json`.
- Stale `token.json` is auto-deleted and OAuth is re-triggered.
- OAuth opens a browser on first run — fails in headless environments.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Error Handling

- Missing `credentials.json`: explain how to obtain it from Google Cloud Console.
- API errors or missing query: print message, exit non-zero.

## Constraints and Exclusions

- Single file (`gmail_search.py`); deps: `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.
- Read-only; no attachment downloads; single account only.
- No pagination — first page (≤100 results) suffices to find the three most recent matches.

## Design Choices

- **Gmail API over IMAP**: no IMAP setup required; reliable, quota-governed.
- **Server-side filter**: `has:attachment` appended to query avoids client-side filtering.
- **`format=metadata`**: fetches headers + MIME structure only, not full message bodies.

## Assumptions and Risks

- Requires a Google Cloud project with Gmail API enabled and `credentials.json` for a desktop OAuth client.
- No retry logic; quota errors (250 units/user/sec) cause exit.
