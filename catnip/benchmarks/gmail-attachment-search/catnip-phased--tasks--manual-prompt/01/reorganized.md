# Spec: Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with the Gmail API, searches a user's mailbox using a query string provided at runtime, and prints a summary of the three most recently received matching emails that contain at least one non-inline attachment.

## Behavior

### Input
- The script accepts a single positional argument: the Gmail search query string (e.g., `"from:boss@example.com subject:report"`).
- Standard Gmail search operators are passed through as-is. The script automatically appends `has:attachment` to the query so users do not need to include it.

### Processing
1. Authenticate with the Gmail API using OAuth 2.0.
2. Issue a `messages.list` call with the combined query (`<user-query> has:attachment`). Gmail's API returns results in reverse-chronological order by default.
3. Take the first three message IDs from the response (most recent first).
4. For each, call `messages.get` with `format=metadata` to fetch headers and part descriptors.

### Output
Plain-text output for each of the (up to) three emails:
- Sender (`From` header)
- Subject
- Date received (`Date` header)
- Attachment filenames and MIME types

Only MIME parts with a non-empty `filename` and `Content-Disposition: attachment` are listed. Inline images (`Content-Disposition: inline`) are excluded, matching user intuition of "attachment."

If fewer than three emails match, print however many were found. If none match, print an informative message and exit with code 0.

## Setup

Requires Python 3.8+.

**Dependencies:**

| Package | Purpose |
|---|---|
| `google-api-python-client` | Gmail REST API wrapper |
| `google-auth-oauthlib` | OAuth 2.0 flow |
| `google-auth-httplib2` | HTTP transport for auth |

```
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

**Authentication:**
- Client credentials are read from `credentials.json` in the working directory (downloaded from Google Cloud Console). This location matches Google's own quickstart examples and is the path of least surprise.
- On first run the browser opens for the OAuth consent flow; the resulting token is cached in `token.json`. The library handles token refresh automatically on subsequent runs.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only; no write access requested).

*Alternative considered:* a service-account credential would avoid browser prompts but requires domain-wide delegation, which is only available on Google Workspace accounts. OAuth 2.0 works for any Gmail account.

## Error Handling

- Missing `credentials.json`: print a setup instruction message and exit with code 1.
- No search query provided: print usage and exit with code 1.
- API errors (network, quota, permission denied): print the error message and exit with code 1.
- Expired/revoked token: the library raises an exception; instruct the user to delete `token.json` and re-run.

## Constraints and Non-Goals

**Assumptions:**
- The user has a Google Cloud project with the Gmail API enabled and has downloaded `credentials.json`.
- The Gmail query syntax is not validated locally; invalid queries return zero results from the API rather than an error.

**Out of scope:**
- Downloading attachment content (only metadata is shown).
- Sending or modifying emails.
- Pagination beyond the first API page (up to 500 results; sufficient for selecting the top 3).
- A GUI or web interface.
