# Gmail Attachment Search Script — Specification

## Overview

A command-line Python script that accepts a Gmail search query from the user, searches their Gmail inbox via the Gmail API, and returns the three most recent matching emails that contain at least one attachment.

---

## Goals

- Simple, single-file script with a clear CLI interface.
- Authenticate once via OAuth 2.0 and cache credentials for subsequent runs.
- Return structured, human-readable output for each result.
- Handle the common failure modes gracefully (no results, no attachments, auth errors).

---

## Non-Goals

- Downloading or saving attachment files to disk (out of scope; print metadata only).
- Pagination beyond retrieving enough results to find 3 with attachments.
- Support for multiple Gmail accounts simultaneously.
- A GUI or web interface.

---

## Inputs

| Input | Source | Description |
|---|---|---|
| `query` | CLI positional argument | A Gmail search query string (same syntax as the Gmail search box, e.g. `from:boss subject:report`). |
| `--max-search` | Optional CLI flag | How many candidate threads to fetch before giving up. Default: `50`. |
| `--credentials` | Optional CLI flag | Path to the OAuth client secrets JSON file. Default: `credentials.json` in the working directory. |
| `--token` | Optional CLI flag | Path to store/read the cached OAuth token. Default: `token.json` in the working directory. |

### Example Invocations

```bash
python gmail_attachments.py "from:alice invoices"
python gmail_attachments.py "subject:report" --max-search 100
python gmail_attachments.py "has:attachment" --credentials ~/my-creds.json
```

---

## Outputs

For each of the (up to 3) matched emails, print a block to stdout:

```
--- Result 1 ---
Message ID : 18f3a2c9d4e1b057
Thread ID  : 18f3a2c9d4e1b057
Date       : 2026-04-10 14:32:07 UTC
From       : alice@example.com
Subject    : Q1 Invoices
Snippet    : Please find attached the Q1 invoice pack…
Attachments:
  1. invoice_q1.pdf  (application/pdf, 142 KB)
  2. summary.xlsx    (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, 38 KB)
```

If fewer than 3 matching emails with attachments are found, print all that exist and note the count:

```
Found 1 email(s) with attachments (fewer than 3).
```

If none are found:

```
No emails matching "<query>" with attachments were found in the first 50 results.
```

---

## Authentication

- Use **OAuth 2.0** with the `google-auth-oauthlib` library.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`
- On first run, open a browser for the user to authorise the application.
- Persist the resulting token to `token.json` (path configurable via `--token`).
- On subsequent runs, load the cached token; refresh automatically if expired.
- If `credentials.json` is missing, print an actionable error message directing the user to the Google Cloud Console and exit with code 1.

---

## Implementation Details

### Dependencies

```
google-api-python-client>=2.0
google-auth-httplib2>=0.1
google-auth-oauthlib>=1.0
```

Provide a `requirements.txt` with pinned major versions.

### High-Level Flow

```
parse_args()
  └─ authenticate()          # load or refresh token; browser flow if needed
       └─ search_messages()  # call messages.list with q=<query>
            └─ for each message (up to --max-search):
                 get_message()          # fetch full message payload
                 has_attachment()       # inspect MIME parts
                 if True → collect()   # extract metadata
                 if len(results) == 3 → break
print_results()
exit(0)
```

### Gmail API Calls

| Step | API method | Key parameters |
|---|---|---|
| Search | `users.messages.list` | `userId='me'`, `q=<query>`, `maxResults=<max-search>` |
| Fetch message | `users.messages.get` | `userId='me'`, `id=<msg_id>`, `format='full'` |

`format='full'` is required to inspect MIME parts and identify attachments.

### Attachment Detection

A message part is considered an attachment if **either** of the following is true:
- `part['filename']` is a non-empty string, **or**
- `part['headers']` contains `Content-Disposition: attachment`.

Recursively walk all `parts` (including nested `multipart/*` payloads).

### Metadata Extraction

For each attachment part, record:
- `filename` — from `part['filename']`; fall back to `"(unnamed)"` if empty.
- `mimeType` — from `part['mimeType']`.
- `size` — from `part['body']['size']` (bytes); convert to KB for display (round to nearest integer).

For the message envelope, extract from the `payload.headers` list:
- `Date`, `From`, `Subject`

Parse the `Date` header into a UTC datetime for display. Sort order relies on the Gmail API returning results in reverse-chronological order (default behaviour of `messages.list`).

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `credentials.json` missing | Print a clear setup message; exit code 1. |
| OAuth token refresh fails | Delete `token.json`, prompt the user to re-run; exit code 1. |
| `googleapiclient.errors.HttpError` | Print the HTTP status and error message; exit code 1. |
| Query returns 0 messages | Print "no results" message; exit code 0. |
| Fewer than 3 results have attachments | Print found results and a count notice; exit code 0. |
| Keyboard interrupt | Print a short cancellation message; exit code 130. |

---

## File Structure

```
gmail-attachments/
├── gmail_attachments.py   # single script; all logic here
├── requirements.txt
├── credentials.json       # user-provided; not committed to VCS
├── token.json             # auto-generated; not committed to VCS
└── spec.md                # this file
```

---

## Setup Instructions (to include in script's `--help`)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Gmail API**.
3. Create an **OAuth 2.0 Client ID** (Desktop app type) and download `credentials.json`.
4. Place `credentials.json` next to `gmail_attachments.py`.
5. Install dependencies: `pip install -r requirements.txt`
6. Run: `python gmail_attachments.py "<your query>"`

---

## Acceptance Criteria

- [ ] Running with a valid query and credentials prints up to 3 email blocks with attachment metadata.
- [ ] Running with a query that matches emails but none have attachments prints the "no attachments found" message.
- [ ] Running without `credentials.json` prints a clear setup error and exits non-zero.
- [ ] A cached `token.json` is used on the second run without re-opening the browser.
- [ ] `--max-search` controls how many messages are inspected before giving up.
- [ ] The script does not download or write attachment data to disk.
