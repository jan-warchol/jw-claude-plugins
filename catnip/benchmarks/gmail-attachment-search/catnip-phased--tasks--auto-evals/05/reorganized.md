# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, searches for emails matching a user-supplied query, and prints the last 3 matching emails that contain at least one attachment.

## Setup

**Dependencies:**
```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

**Authentication:**
- Requires a `credentials.json` file (downloaded from Google Cloud Console) in the working directory.
- On first run, opens a browser for OAuth2 consent and saves credentials to `token.json`.
- On subsequent runs, loads `token.json`, refreshing the access token automatically if expired.
- Scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only; no send, delete, or modify access).

## Interface

**Invocation:**
```bash
python gmail_search.py "<query>"
```

**Query string** (required positional argument): any valid Gmail search query. The query is passed to the API as-is — not modified or extended by the script.

Examples:
```bash
python gmail_search.py "from:alice subject:invoice"
python gmail_search.py "has:attachment newer_than:7d"
```

## Behavior

1. Authenticate with the Gmail API.
2. Search messages using the provided query, requesting up to 100 results sorted by most-recent first (default Gmail API ordering).
3. For each result (newest first), fetch the full message payload (`format=full`) and inspect MIME parts.
4. Collect the first 3 messages that have at least one true attachment: a MIME part where `Content-Disposition` is `attachment`, **or** the part carries a non-empty `filename` and is not flagged as `inline`. Inline images embedded in HTML emails are excluded.
5. Stop once 3 qualifying messages are found or the 100-result page is exhausted — no further pagination.
6. Print results.

### Output

For each of the (up to) 3 qualifying emails:

```
Subject: <subject>
From:    <sender>
Date:    <date as provided by Gmail>
Attachments:
  - <filename> (<mime-type>, <size> bytes)
---
```

If an attachment has no filename, display `(unnamed)`. If no qualifying emails are found:

```
No emails with attachments found matching: <query>
```

### Error Handling

- Missing `credentials.json`: print a clear message explaining where to obtain it; exit code 1.
- Expired/revoked `token.json`: surface a clear re-authentication prompt; exit code 1.
- Gmail API errors (network, quota): print the error; exit code 1.
- Invalid or empty query: accepted as-is; Gmail returns zero results, triggering the "no results" message.

## Design Notes

**Query passed as-is:** The script does not append `has:attachment` automatically. This keeps the query transparent and composable — users may already include it, or may want unfiltered results. The trade-off is slightly more API calls when matching emails lack attachments.

**No pagination beyond 100 results:** Fetching further pages multiplies API calls. For a simple utility, 100 results is a reasonable bound; users needing deeper search can narrow their query.

**`format=full` per message:** Simpler than a two-step metadata-then-body fetch. The cost is larger response payloads, acceptable since at most 3 full messages are fetched.

**Exclusions:**
- Does not download attachment content — metadata only (filename, MIME type, size).
- Does not support multiple Gmail accounts or service-account authentication.
- Result count is fixed at 3; no `--limit` flag.
- No machine-readable (JSON) output mode.

**Assumptions and risks:**
- First-run OAuth requires a local browser; headless environments need manual token setup.
- API quota: listing 100 headers + fetching 3 full messages stays well within the 250 units/second default limit.
- `token.json` contains a long-lived refresh token — treat it like a password and exclude from version control.
