# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, searches for emails matching a user-supplied query, and prints the last 3 matching emails that contain at least one attachment.

## Authentication

- Uses the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- On first run, opens a browser for OAuth2 consent and saves credentials to `token.json`.
- On subsequent runs, loads credentials from `token.json`, refreshing the access token automatically if expired.
- Requires a `credentials.json` file (downloaded from Google Cloud Console) in the working directory.
- Scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only; no send, delete, or modify access).

## Inputs

- **Query string**: passed as a command-line argument (required). Any valid Gmail search query is accepted (e.g. `from:alice subject:invoice`).

## Behavior

1. Authenticate with the Gmail API.
2. Search messages using the provided query **as-is** (the query is not modified), requesting up to 100 results sorted by most-recent first (default Gmail API ordering).
3. For each result (newest first), fetch the full message payload and inspect MIME parts.
4. Collect the first 3 messages that have at least one true attachment: a MIME part where `Content-Disposition` is `attachment` **or** the part carries a non-empty `filename` and is not flagged as `inline`. Inline images embedded in HTML emails are excluded.
5. Stop once 3 qualifying messages are found or the 100-result page is exhausted — no further pagination.
6. Print the results (see Output section).

## Output

For each of the (up to) 3 qualifying emails, print:

```
Subject: <subject>
From:    <sender>
Date:    <date as provided by Gmail>
Attachments:
  - <filename> (<mime-type>, <size> bytes)
---
```

If an attachment has no filename, display `(unnamed)`.

If no matching emails with attachments are found, print:

```
No emails with attachments found matching: <query>
```

## Error Handling

- Missing `credentials.json`: print a clear error message explaining where to obtain the file and exit with code 1.
- Gmail API errors (network issues, quota exceeded): print the error and exit with code 1.
- Invalid or empty query: accepted as-is; Gmail will return zero results, triggering the "no results" message.
- Expired/revoked `token.json`: the library raises an exception; surface it as a clear re-authentication prompt and exit with code 1.

## Design Choices and Trade-offs

**Query passed as-is vs. auto-appending `has:attachment`:** The script does not append `has:attachment` to the user's query. This lets the user control the search precisely (they may already include `has:attachment`, or may want results without it for debugging). The trade-off is slightly more API calls when results include non-attachment emails. The benefit is transparency and composability.

**No pagination beyond 100 results:** Fetching additional pages would multiply API calls. For a simple utility, 100 results is a reasonable bound; users needing deeper search can narrow their query.

**`format=full` per message:** Fetching the full payload in one call is simpler than fetching metadata first and body second. The cost is larger response payloads, acceptable for a script processing at most 3 messages.

## Explicit Exclusions

- Does not download attachment content — only lists metadata (filename, MIME type, size).
- Does not support multiple Gmail accounts or service-account authentication.
- Does not support `--limit` or configurable result count; the count is fixed at 3.
- No JSON or machine-readable output mode.

## Assumptions and Risks

- **Browser available**: the first-run OAuth flow requires a local browser. Headless environments need manual token setup.
- **API quota**: each `messages.get` call costs ~5 quota units; fetching up to 100 message headers plus up to 3 full bodies stays well within the default 250 units/second limit.
- **`token.json` security**: the file contains a long-lived refresh token. Users should treat it like a password and not commit it to version control.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Usage Example

```bash
python gmail_search.py "from:alice subject:invoice"
python gmail_search.py "has:attachment newer_than:7d"
```
