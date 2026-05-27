# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with the Gmail API, searches for emails matching a user-supplied query string, and prints the most recent 3 results that contain at least one attachment.

---

## Inputs

| Input | Source | Notes |
|---|---|---|
| Search query | CLI argument (`sys.argv[1]`) or prompted interactively | Passed directly to Gmail API `q` parameter |
| OAuth credentials file | `credentials.json` in working directory | Downloaded from Google Cloud Console |

---

## Authentication

- Uses **OAuth 2.0** via `google-auth-oauthlib`.
- Scopes: `https://www.googleapis.com/auth/gmail.readonly`
- Token cached in `token.json` in the working directory; refreshed automatically on expiry.
- First run opens a browser for the user to complete the OAuth consent flow.

---

## Core Logic

1. Parse the query from the command line (positional arg; error and exit if missing).
2. Build an authenticated Gmail API service (`googleapiclient.discovery.build`).
3. Call `users.messages.list` with the query; paginate if needed to collect enough candidates.
4. For each message candidate (newest first):
   a. Fetch the full message (`users.messages.get`, `format=metadata`, headers + parts).
   b. Check whether any part has a `filename` that is non-empty — that signals an attachment.
   c. Collect the message if it has at least one attachment.
   d. Stop once 3 such messages have been found.
5. For each of the up to 3 collected messages, print a formatted summary (see Output section).

---

## Output

Printed to stdout. For each matching email:

```
--- Email 1 ---
Date:    Mon, 26 May 2026 14:32:01 +0000
From:    Alice <alice@example.com>
Subject: Q2 Report
Attachments:
  - report.pdf (application/pdf)
  - data.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
```

If fewer than 3 emails with attachments are found, only the available ones are shown.

If no matching emails with attachments are found:

```
No emails with attachments found for query: "<query>"
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing query argument | Print usage message and exit with code 1 |
| `credentials.json` not found | Print clear error message and exit with code 1 |
| Gmail API error (HTTP 4xx/5xx) | Catch `googleapiclient.errors.HttpError`, print error details, exit with code 1 |
| Token refresh failure | Surface the underlying exception message, exit with code 1 |

---

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Install via:

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## File Layout

```
gmail_attachment_search.py   # the script
credentials.json             # OAuth client secret (user must supply)
token.json                   # cached OAuth token (auto-generated on first run)
```

---

## Non-goals

- Downloading attachment content.
- Searching multiple Gmail accounts.
- GUI or web interface.
- Pagination beyond what is needed to find 3 matches.
