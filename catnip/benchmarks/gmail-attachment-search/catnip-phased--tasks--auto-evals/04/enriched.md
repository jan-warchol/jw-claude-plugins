# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with the Gmail API, searches for emails matching a user-supplied query string, and prints the most recent 3 results that contain at least one attachment. "Most recent" is defined by Gmail's default message ordering (newest received first).

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
3. Call `users.messages.list` with the query; Gmail returns results newest-first by default. Paginate using `nextPageToken` only as long as fewer than 3 attachment-bearing messages have been found, to avoid unnecessary API calls.
4. For each message candidate:
   a. Fetch the message with `users.messages.get`, `format=metadata`, requesting headers `Date`, `From`, `Subject` plus `metadataHeaders`. This avoids downloading full MIME bodies.
   b. Walk the `payload.parts` tree (recursively for multipart messages). A part signals an attachment when its `filename` field is non-empty. Inline images that have a non-empty `filename` are counted as attachments.
   c. Collect the message if at least one such part is found.
   d. Stop once 3 such messages have been found.
5. Print a formatted summary for each collected message.

### Design choices

- **`format=metadata` over `format=full`**: avoids downloading message bodies and base64-encoded attachments; MIME structure metadata is sufficient to detect attachments and read headers.
- **User controls the query**: the script does not automatically append `has:attachment` to the query. This keeps behavior predictable — the user can include it themselves if desired, and post-filtering against the actual MIME structure remains the authoritative check.
- **`sys.argv[1]` over argparse**: the interface is a single positional argument; argparse adds no value here for a one-arg script.

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

Missing headers (`Date`, `From`, `Subject`) are printed as `(unknown)`. MIME type is shown if available, omitted otherwise.

If fewer than 3 matches are found, only the available ones are shown. If none:

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

## Assumptions and Risks

- **Python 3.8+** is assumed; no compatibility shims for older versions.
- The user must have a Google Cloud project with the Gmail API enabled and an OAuth 2.0 Desktop client configured before running the script for the first time. Setup steps are out of scope but should be noted in usage docs.
- If the query matches many emails but very few have attachments, the script may make many API calls (one `messages.get` per candidate). This is acceptable for a simple tool; no rate-limit backoff is implemented.
- Gmail API quotas (per-user: 250 quota units/second; `messages.get` costs 5 units) are unlikely to be hit in normal use given the 3-result limit.

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
- Rate-limit backoff or retry logic.
