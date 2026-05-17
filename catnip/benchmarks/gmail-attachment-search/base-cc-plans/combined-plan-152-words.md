# Plan: Gmail Attachment Search Script

## Overview

A Python 3.8+ CLI script using `google-api-python-client` with OAuth 2.0. Accepts a search query,
appends `has:attachment` for server-side filtering, and prints the 3 most recent matching messages.
Single file `search_gmail.py`; `credentials.json` and auto-generated `token.json` both gitignored;
dependencies in `requirements.txt` (`google-api-python-client`, `google-auth-httplib2`,
`google-auth-oauthlib`).

## Steps

1. **Google Cloud Setup** — Enable Gmail API, create OAuth 2.0 Desktop App credentials, download
   `credentials.json`.
2. **Authentication** — Check for cached `token.json`; if missing or expired, run OAuth browser flow
   and save token. Scope: `gmail.readonly`.
3. **Search** — Build `f"({user_query}) has:attachment"`, call
   `messages.list(userId="me", q=query, maxResults=3)`.
4. **Fetch & Output** — For each ID, call `messages.get(format="full")` to extract `From`,
   `Subject`, `Date` and attachment filenames from `payload.parts`. Print a `--- Email N ---`
   summary. Accept query via `argparse`, fallback to interactive prompt.

## Error Handling

- `credentials.json` missing: print setup instructions and exit.
- Token refresh failure: delete `token.json` and prompt re-authentication.
- API/network error: catch `HttpError`, print message, exit cleanly.

## Out of Scope

- Downloading attachments
- Pagination
- Multiple accounts
- Sending or modifying emails
