# Gmail Attachment Search — Spec

## Overview

A Python command-line script that authenticates with Gmail, accepts a user-provided search query, and returns the three most recent emails matching that query which contain at least one attachment. "Most recent" is defined by Gmail's `internalDate` field (server receipt time), which is the natural ordering returned by the API.

---

## Functional Requirements

1. **Authentication** — Authenticate with the Gmail API using OAuth 2.0. On first run, launch a browser-based consent flow and cache credentials locally for subsequent runs.
2. **Query input** — Accept the search query as a command-line argument (positional or `--query`). An empty or whitespace-only query is rejected with a usage error before any API call is made.
3. **Search** — Submit the query to the Gmail API (using Gmail's standard search syntax, e.g. `from:alice has:attachment`). Append `has:attachment` to the query only if it is not already present, to avoid duplication and redundant tokens.
4. **Result limit** — Retrieve up to the 3 most recent matching emails.
5. **Output** — For each matched email print:
   - Date received
   - Sender (`From`)
   - Subject
   - List of attachment filenames and their MIME types
6. **No-result handling** — If fewer than 3 (or zero) emails match, return however many do and report the count clearly.

### Definition of "Attachment"

Only message parts with a non-inline `Content-Disposition` (i.e. `attachment`) or with a `filename` in their MIME metadata are counted as attachments. Inline images embedded in HTML bodies (Content-Disposition: `inline`) are excluded. This matches the user's intuitive expectation of a downloadable file.

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
| Empty query | Print usage error before any API call; exit 1 |
| Zero results | Print "No emails found matching `<query>` with attachments." |
| API quota exceeded | Print the error message from the API response; exit 1 |
| Network error | Print "Network error: <detail>"; exit 1 |
| Invalid/expired token + refresh failure | Delete `token.json`, prompt re-auth |

---

## Trade-offs and Rejected Alternatives

**Gmail API vs IMAP** — The Gmail API is chosen over IMAP because it supports Gmail's full search syntax (labels, operators like `has:attachment`, `from:`, etc.) natively. IMAP search is limited and would require client-side filtering for many query types.

**OAuth InstalledAppFlow vs Service Account** — A service account requires Google Workspace domain delegation and is unsuitable for personal Gmail accounts. OAuth with InstalledAppFlow works for any Google account and is the standard path for desktop scripts.

**`format=metadata` vs `format=full`** — `format=metadata` returns headers and MIME structure without attachment data, keeping responses small. Full message bodies are not needed to list attachment names and types.

---

## Risks, Assumptions, and Open Questions

- **Assumes Python 3.8+** — f-strings and `pathlib` are used freely; no older Python compatibility.
- **Assumes a browser is available** — the OAuth consent flow opens a local browser tab. Headless environments are not supported.
- **Prerequisite: Google Cloud project** — the user must have created a project, enabled the Gmail API, and downloaded `credentials.json`. The script cannot create this for them.
- **API quota** — Gmail API has per-user read quotas (default 250 quota units/second). Three message fetches use minimal quota and are unlikely to hit limits.
- **Open question: attachment name collisions** — if two parts share a filename, both are listed as-is with no disambiguation.

---

## Out of Scope

- Downloading attachment content
- Sending or modifying emails
- Pagination beyond the first page of results
- GUI or web interface
- Google Workspace service account authentication
- Multi-account support
