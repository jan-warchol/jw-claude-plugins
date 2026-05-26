# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, accepts a search query from the user, and prints the 3 most recent emails matching that query which contain at least one attachment.

## Setup

### Prerequisites

- Python 3.8+.
- A Google Cloud project with the Gmail API enabled and an OAuth 2.0 client ID downloaded as `credentials.json`.
- A browser available on first run for the OAuth consent flow.
- A personal or Workspace Gmail account where the user has granted API access.

### Authentication

- Uses Google OAuth 2.0 via `google-auth` and `google-auth-oauthlib`; scope: `gmail.readonly`.
- First run opens a browser for the consent flow. The token is cached in `token.json` and refreshed automatically on expiry.

### Files & Dependencies

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (not committed)
token.json                   # cached token (not committed, auto-generated)
```

Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Behavior

### Input

The search query is accepted as a positional CLI argument; if omitted, the script prompts interactively. Example: `from:boss subject:invoice`.

### Logic

1. Authenticate and build the Gmail API client.
2. Append `has:attachment` to the user query (skipped if already present, case-insensitive), then call `users.messages.list` with `maxResults=3`.
3. For each returned message ID, call `users.messages.get` with `format=metadata` and `metadataHeaders=[Subject, From, Date]`.
4. Extract attachment filenames from `payload.parts` where `filename` is non-empty.
5. Print a summary for each email (see Output).

### Output

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date as returned by Gmail>
    Attachments: <filename1>, <filename2>, …
```

If fewer than 3 matches exist, print however many were found. If none: `No matching emails with attachments found.`

## Error Handling

- Missing `credentials.json`: print a setup message directing the user to the Google Cloud Console, exit non-zero.
- Token refresh failure: surface the error and prompt the user to delete `token.json` and re-authenticate.
- API errors (HTTP 4xx/5xx): surface the error message and exit non-zero.
- No results: handled gracefully (see Output).

## Design Notes

### Decisions & Trade-offs

- **OAuth 2.0 vs. service account**: OAuth is correct for personal Gmail; service accounts require Workspace domain delegation.
- **`format=metadata` vs. `format=full`**: Metadata fetches only headers and part structure — sufficient here and keeps responses small.
- **`has:attachment` appended by script**: Guarantees the constraint is always applied while avoiding duplication when the user already includes it.
- **Hard-coded limit of 3**: Matches the requirement; no override flag is provided.

### Out of Scope

- Downloading attachment content.
- Pagination beyond the first page of results.
- Multiple Gmail accounts simultaneously.
- Configurable result count.
- Filtering by attachment type or size.
