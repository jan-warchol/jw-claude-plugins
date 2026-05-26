# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, accepts a search query from the user, and prints the last 3 emails matching that query which contain at least one attachment. "Last 3" means the 3 most recent by Gmail's default sort order (newest first).

## Authentication

- Uses Google OAuth 2.0 via `google-auth` and `google-auth-oauthlib`.
- Credentials stored in `credentials.json` (downloaded from Google Cloud Console).
- Token cached in `token.json` after first successful login; refreshed automatically on expiry.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- First run opens a browser for the consent flow; subsequent runs use the cached token silently.

## Inputs

| Source | Name | Description |
|--------|------|-------------|
| CLI arg / prompt | `query` | Gmail search string (e.g. `from:boss subject:invoice`). Passed as a positional argument; if omitted, the script prompts interactively. |

The script appends `has:attachment` to the query before calling the API, unless the user's query already contains it (case-insensitive check), to avoid redundant filtering.

## Core Logic

1. Authenticate and build the Gmail API client.
2. Call `users.messages.list` with the combined query (user query + `has:attachment`), `maxResults=3`.
3. For each returned message ID, call `users.messages.get` with `format=metadata` and `metadataHeaders=[Subject, From, Date]` to retrieve headers and part metadata (for attachment filenames).
4. Extract attachment filenames from `payload.parts` where `filename` is non-empty.
5. Print a summary for each email.

## Output

For each of the (up to 3) matching emails, print to stdout:

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date as returned by Gmail>
    Attachments: <filename1>, <filename2>, …
```

If fewer than 3 matches exist, print however many were found. If none, print `No matching emails with attachments found.`

## Design Decisions & Trade-offs

- **OAuth 2.0 vs. service account**: OAuth is the standard choice for scripts acting on behalf of a personal Gmail user. Service accounts require Workspace domain delegation — overkill here.
- **`format=metadata` vs. `format=full`**: Metadata fetches only headers and part structure, not the full body, keeping responses small. Sufficient since we only need subject, sender, date, and attachment names.
- **Hard-coded result limit of 3**: Matches the stated requirement; no flag to override is provided (out of scope).
- **`has:attachment` appended by script**: Ensures the constraint is always applied even if the user forgets it, while avoiding duplication.

## Assumptions

- Python 3.8+.
- The user has a Google Cloud project with the Gmail API enabled and an OAuth 2.0 client ID downloaded as `credentials.json`.
- A browser is available on first run for the OAuth consent flow.
- The Gmail account is a personal or Workspace account where the user has granted API access.

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to the Google Cloud Console, exit non-zero.
- Token refresh failure: surface the error and prompt the user to delete `token.json` and re-authenticate.
- API errors (HTTP 4xx/5xx): surface the error message and exit with a non-zero code.
- No results: handled gracefully (see Output section).

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Files

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (not committed)
token.json                   # cached token (not committed, auto-generated)
```

## Out of Scope

- Downloading attachment content.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts simultaneously.
- Configurable result count.
- Filtering by attachment type or size.
