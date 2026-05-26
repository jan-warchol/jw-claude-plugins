# Gmail Attachment Search — Spec

## Overview

A Python command-line script that authenticates with Gmail, accepts a user-provided search query, and returns the three most recent emails matching that query which contain at least one attachment.

---

## Functional Requirements

1. **Authentication** — Authenticate with the Gmail API using OAuth 2.0. On first run, launch a browser-based consent flow and cache credentials locally for subsequent runs.
2. **Query input** — Accept the search query as a command-line argument (positional or `--query`).
3. **Search** — Submit the query to the Gmail API (using Gmail's standard search syntax, e.g. `from:alice has:attachment`). Additionally apply a `has:attachment` filter to the query to pre-filter results server-side.
4. **Result limit** — Retrieve up to the 3 most recent matching emails.
5. **Output** — For each matched email print:
   - Date received
   - Sender (`From`)
   - Subject
   - List of attachment filenames and their MIME types
6. **No-result handling** — If fewer than 3 (or zero) emails match, return however many do and report the count clearly.

---

## Non-Functional Requirements

- **Simplicity** — Single script file, minimal dependencies.
- **Credentials security** — OAuth token stored in a local file (`token.json`); credentials file (`credentials.json`) provided by user. Neither is committed to version control.
- **Error messages** — Clear, human-readable errors for common failure modes (missing credentials file, invalid query, network error, quota exceeded).

---

## Technical Design

### Dependencies

| Package | Purpose |
|---|---|
| `google-auth-oauthlib` | OAuth 2.0 flow |
| `google-auth-httplib2` | HTTP transport |
| `google-api-python-client` | Gmail REST API client |

Install via: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`

### Gmail API Scopes

`https://www.googleapis.com/auth/gmail.readonly` — read-only access is sufficient.

### Search Strategy

Append `has:attachment` to the user's query before submitting, so the API pre-filters. Example: user provides `from:alice invoice` → submitted as `from:alice invoice has:attachment`.

Use `users.messages.list` with `maxResults=3` and `q=<modified_query>`. Then fetch each message with `users.messages.get` using `format=metadata` to extract headers and part metadata (avoiding downloading full attachment bodies).

### Credential Bootstrap

1. Check for `token.json`; if present, load and refresh if expired.
2. If absent or invalid, run `InstalledAppFlow` from `credentials.json` (path configurable via `--credentials` flag, default `./credentials.json`).
3. Save refreshed/new token back to `token.json`.

---

## CLI Interface

```
python gmail_attachment_search.py "your search query"

Options:
  --credentials PATH   Path to credentials.json  [default: ./credentials.json]
  --token PATH         Path to token cache file   [default: ./token.json]
```

---

## Output Format

```
Found 3 email(s) matching "<query>" with attachments:

1. 2024-03-15  From: alice@example.com
   Subject: Q1 Invoice
   Attachments:
     - invoice_q1.pdf  (application/pdf)

2. ...
```

---

## Error Cases

| Condition | Behaviour |
|---|---|
| `credentials.json` not found | Print instructions for creating a Google Cloud project and downloading credentials; exit 1 |
| Zero results | Print "No emails found matching `<query>` with attachments." |
| API quota exceeded | Print the error message from the API response; exit 1 |
| Network error | Print "Network error: <detail>"; exit 1 |
| Invalid/expired token + refresh failure | Delete `token.json`, prompt re-auth |

---

## Out of Scope

- Downloading attachment content
- Sending or modifying emails
- Pagination beyond the first page of results
- GUI or web interface
