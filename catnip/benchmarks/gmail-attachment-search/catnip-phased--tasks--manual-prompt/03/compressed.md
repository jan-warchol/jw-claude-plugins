# Gmail Attachment Search — Spec

## Overview

CLI Python script: authenticates via Gmail OAuth 2.0, takes a search query, prints the 3 most recent matching emails that have attachments.

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud project with Gmail API enabled; OAuth 2.0 client ID saved as `credentials.json`
- Browser available for first-run consent flow
- Personal or Workspace Gmail account with API access granted

### Authentication

OAuth 2.0 via `google-auth`/`google-auth-oauthlib`; scope: `gmail.readonly`. First run opens browser for consent; token cached in `token.json`, auto-refreshed on expiry.

### Files & Dependencies

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (not committed)
token.json                   # cached token (not committed, auto-generated)
```

Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Behavior

### Input

Positional CLI argument; script prompts if omitted. Example: `from:boss subject:invoice`.

### Logic

1. Authenticate and build the Gmail API client.
2. Append `has:attachment` to the query (skipped if already present, case-insensitive); call `users.messages.list` with `maxResults=3`.
3. For each message ID, call `users.messages.get` with `format=metadata`, `metadataHeaders=[Subject, From, Date]`.
4. Extract attachment filenames from `payload.parts` where `filename` is non-empty.
5. Print summary (see Output).

### Output

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date as returned by Gmail>
    Attachments: <filename1>, <filename2>, …
```

Prints however many results exist (up to 3). If none: `No matching emails with attachments found.`

## Error Handling

- Missing `credentials.json`: direct user to Google Cloud Console, exit non-zero.
- Token refresh failure: surface error, prompt user to delete `token.json` and re-authenticate.
- API error (4xx/5xx): surface message, exit non-zero.

## Design Notes

### Decisions & Trade-offs

- **OAuth vs. service account**: OAuth is correct for personal Gmail; service accounts need Workspace domain delegation.
- **`format=metadata` vs. `full`**: metadata returns only headers and part structure — sufficient and lightweight.
- **`has:attachment` appended by script**: always enforces the constraint; skips it if the user already included it.
- **Limit hard-coded to 3**: per requirement; no override flag.

### Out of Scope

Downloading attachments · pagination · multiple accounts · configurable result count · filtering by attachment type/size.
