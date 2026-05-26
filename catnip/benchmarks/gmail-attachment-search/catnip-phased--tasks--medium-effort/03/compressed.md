# Gmail Attachment Search — Spec

## Overview

A Python CLI script that authenticates with Gmail, accepts a search query, and prints the 3 most recent matching emails that have attachments. Recency is determined by Gmail's `internalDate` (server receipt time), the API's natural ordering.

---

## Functional Requirements

1. **Authentication** — OAuth 2.0 via browser consent on first run; credentials cached locally for subsequent runs.
2. **Query input** — Positional CLI argument (or `--query`). Empty/whitespace query → usage error before any API call.
3. **Search** — Submit using Gmail's search syntax. Append `has:attachment` only if not already present in the query.
4. **Result limit** — Up to 3 most recent matching emails.
5. **Output** — Per email: date received, sender, subject, attachment filenames and MIME types.
6. **Partial results** — Fewer than 3 matches returned as-is with count reported.

### Definition of "Attachment"

Parts with `Content-Disposition: attachment` or a `filename` in MIME metadata. Inline images (`Content-Disposition: inline`) are excluded.

---

## Non-Functional Requirements

- **Simplicity** — Single script file, minimal dependencies.
- **Security** — `token.json` and `credentials.json` are local files; neither committed to version control.
- **Errors** — Human-readable messages for all common failures.

---

## Technical Design

### Dependencies

| Package | Purpose |
|---|---|
| `google-auth-oauthlib` | OAuth 2.0 flow |
| `google-auth-httplib2` | HTTP transport |
| `google-api-python-client` | Gmail API client |

`pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`

### API Usage

- Scope: `https://www.googleapis.com/auth/gmail.readonly`
- List: `users.messages.list` with `maxResults=3`, `q=<query> has:attachment`
- Fetch: `users.messages.get` with `format=metadata` (headers + MIME structure; no attachment bodies downloaded)

### Credential Bootstrap

1. Load `token.json` if present; refresh if expired.
2. Otherwise run `InstalledAppFlow` from `credentials.json`.
3. Save token back to `token.json`.

Paths configurable via `--credentials` and `--token` flags.

---

## CLI Interface

```
python gmail_attachment_search.py "your search query"
  --credentials PATH   [default: ./credentials.json]
  --token PATH         [default: ./token.json]
```

## Output Format

```
Found 3 email(s) matching "<query>" with attachments:

1. 2024-03-15  From: alice@example.com
   Subject: Q1 Invoice
   Attachments:
     - invoice_q1.pdf  (application/pdf)
```

---

## Error Cases

| Condition | Behaviour |
|---|---|
| `credentials.json` missing | Print setup instructions; exit 1 |
| Empty query | Print usage error; exit 1 |
| Zero results | Print "No emails found matching `<query>` with attachments." |
| Quota exceeded / network error | Print API/network error detail; exit 1 |
| Token expired + refresh failure | Delete `token.json`, prompt re-auth |

---

## Trade-offs

- **Gmail API over IMAP** — supports Gmail's full search syntax natively; IMAP search requires client-side filtering.
- **OAuth InstalledAppFlow over service account** — service accounts need Workspace domain delegation; OAuth works for any personal Google account.
- **`format=metadata` over `format=full`** — returns headers and MIME structure only, avoiding unnecessary attachment data transfer.

---

## Risks and Assumptions

- **Python 3.8+** required (f-strings, `pathlib`).
- **Browser required** for OAuth consent flow; headless environments unsupported.
- **Prerequisite**: user must supply `credentials.json` from a Google Cloud project with the Gmail API enabled.
- **Quota**: 3 fetches use negligible quota (limit: 250 units/second per user).
- **Filename collisions**: duplicate attachment names listed as-is, no disambiguation.

---

## Out of Scope

- Downloading attachment content
- Sending or modifying emails
- Pagination beyond first result page
- GUI / web interface
- Service account auth, multi-account support
