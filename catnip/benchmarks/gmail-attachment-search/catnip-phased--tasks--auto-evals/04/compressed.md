# Gmail Attachment Search — Spec

## Overview

CLI Python script: authenticates with the Gmail API, searches emails by a user-supplied query, and prints the 3 most recent results (newest received first) that have at least one attachment.

---

## Setup

**Requirements:** Python 3.8+; Google Cloud project with Gmail API enabled and an OAuth 2.0 Desktop client configured (out of scope, must be done before first run).

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

```
gmail_attachment_search.py   # the script
credentials.json             # OAuth client secret (user must supply)
token.json                   # cached token (auto-generated on first run)
```

---

## Authentication

OAuth 2.0 via `google-auth-oauthlib`, scope `gmail.readonly`. `credentials.json` must be in the working directory. First run opens a browser for consent; token is cached in `token.json` and auto-refreshed on expiry.

---

## Interface

**Input:** Single positional arg — the query string (`sys.argv[1]`), passed directly to the Gmail API `q` parameter.

**Output** (stdout):

```
--- Email 1 ---
Date:    Mon, 26 May 2026 14:32:01 +0000
From:    Alice <alice@example.com>
Subject: Q2 Report
Attachments:
  - report.pdf (application/pdf)
  - data.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
```

Missing headers print as `(unknown)`; MIME type is omitted if unavailable. Fewer than 3 results are shown when fewer match. If none:

```
No emails with attachments found for query: "<query>"
```

---

## Core Logic

1. Parse query from CLI; exit with code 1 if missing.
2. Build Gmail API service via `googleapiclient.discovery.build`.
3. Call `users.messages.list` with the query (results are newest-first by default). Paginate via `nextPageToken` only until 3 attachment-bearing messages are found.
4. Per candidate: fetch with `users.messages.get` (`format=metadata`, headers `Date`/`From`/`Subject`); recursively walk `payload.parts`; treat any part with a non-empty `filename` as an attachment (includes inline images). Collect if at least one found; stop at 3.
5. Print a formatted summary for each collected message.

### Design choices

- **`format=metadata`:** avoids downloading bodies and base64 attachment data; MIME metadata suffices for detection and headers.
- **User controls query:** no automatic `has:attachment` appended; the user may add it for efficiency, but MIME post-filtering is the authoritative check.
- **`sys.argv[1]`:** a single positional arg warrants no argparse.
- **API call volume:** sparse-attachment queries may issue many `messages.get` calls (5 quota units each; 250 units/sec limit). Acceptable for a simple tool; no backoff implemented.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing query argument | Print usage, exit 1 |
| `credentials.json` not found | Print error, exit 1 |
| Gmail API error (4xx/5xx) | Catch `HttpError`, print details, exit 1 |
| Token refresh failure | Print exception message, exit 1 |

---

## Non-goals

- Downloading attachment content.
- Multiple Gmail accounts.
- GUI or web interface.
- Pagination beyond finding 3 matches.
- Rate-limit backoff.
