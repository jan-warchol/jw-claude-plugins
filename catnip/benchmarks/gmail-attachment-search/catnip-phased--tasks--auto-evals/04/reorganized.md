# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with the Gmail API, searches for emails matching a user-supplied query string, and prints the most recent 3 results that contain at least one attachment. "Most recent" is defined by Gmail's default message ordering (newest received first).

---

## Setup

**Requirements:** Python 3.8+; a Google Cloud project with the Gmail API enabled and an OAuth 2.0 Desktop client configured (steps are out of scope but must be completed before first run).

**Install dependencies:**

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Files:**

```
gmail_attachment_search.py   # the script
credentials.json             # OAuth client secret (user must supply)
token.json                   # cached OAuth token (auto-generated on first run)
```

---

## Authentication

- Uses **OAuth 2.0** via `google-auth-oauthlib`, scope `https://www.googleapis.com/auth/gmail.readonly`.
- `credentials.json` (OAuth client secret) must be present in the working directory.
- On first run, a browser opens for the consent flow; the resulting token is cached in `token.json` and refreshed automatically on expiry.

---

## Interface

**Input:** A single positional CLI argument — the search query string (`sys.argv[1]`). It is passed directly to the Gmail API `q` parameter, giving the user full control over Gmail query syntax.

**Output:** Printed to stdout. For each matching email:

```
--- Email 1 ---
Date:    Mon, 26 May 2026 14:32:01 +0000
From:    Alice <alice@example.com>
Subject: Q2 Report
Attachments:
  - report.pdf (application/pdf)
  - data.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
```

Missing headers (`Date`, `From`, `Subject`) are printed as `(unknown)`. MIME type is shown if available, omitted otherwise.

If fewer than 3 matches are found, only the available ones are shown. If none:

```
No emails with attachments found for query: "<query>"
```

---

## Core Logic

1. Parse the query from the command line (positional arg; error and exit if missing).
2. Build an authenticated Gmail API service (`googleapiclient.discovery.build`).
3. Call `users.messages.list` with the query; Gmail returns results newest-first by default. Paginate using `nextPageToken` only as long as fewer than 3 attachment-bearing messages have been found, to avoid unnecessary API calls.
4. For each message candidate:
   a. Fetch the message with `users.messages.get`, `format=metadata`, requesting headers `Date`, `From`, `Subject`. This avoids downloading full MIME bodies.
   b. Walk the `payload.parts` tree (recursively for multipart messages). A part signals an attachment when its `filename` field is non-empty. Inline images with a non-empty `filename` are counted as attachments.
   c. Collect the message if at least one such part is found.
   d. Stop once 3 such messages have been found.
5. Print a formatted summary for each collected message.

### Design choices

- **`format=metadata` over `format=full`:** avoids downloading bodies and base64-encoded attachment data; MIME structure metadata is sufficient to detect attachments and read headers.
- **User controls the query:** the script does not automatically append `has:attachment`. The user may include it for efficiency; post-filtering against the actual MIME structure is the authoritative check regardless.
- **`sys.argv[1]` over argparse:** a single positional argument needs no argument-parsing library.
- **API call volume:** if the query matches many emails but few have attachments, the script may issue many `messages.get` calls (5 quota units each; per-user limit is 250 units/second). This is acceptable for a simple tool; no backoff is implemented.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing query argument | Print usage message and exit with code 1 |
| `credentials.json` not found | Print clear error message and exit with code 1 |
| Gmail API error (HTTP 4xx/5xx) | Catch `googleapiclient.errors.HttpError`, print error details, exit with code 1 |
| Token refresh failure | Surface the underlying exception message, exit with code 1 |

---

## Non-goals

- Downloading attachment content.
- Searching multiple Gmail accounts.
- GUI or web interface.
- Pagination beyond what is needed to find 3 matches.
- Rate-limit backoff or retry logic.
