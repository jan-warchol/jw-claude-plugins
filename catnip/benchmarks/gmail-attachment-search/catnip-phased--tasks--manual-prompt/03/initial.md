# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, accepts a search query from the user, and prints the last 3 emails matching that query which contain at least one attachment.

## Authentication

- Uses Google OAuth 2.0 via `google-auth` and `google-auth-oauthlib`.
- Credentials stored in `credentials.json` (downloaded from Google Cloud Console).
- Token cached in `token.json` after first successful login; refreshed automatically on expiry.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Inputs

| Source | Name | Description |
|--------|------|-------------|
| CLI arg / prompt | `query` | Gmail search string (e.g. `from:boss subject:invoice`). Passed as a positional argument; if omitted, the script prompts interactively. |

## Core Logic

1. Authenticate and build the Gmail API client.
2. Call `users.messages.list` with the user-supplied query plus the implicit filter `has:attachment`, fetching up to the most recent 3 results (`maxResults=3`).
3. For each returned message ID, call `users.messages.get` with `format=metadata` to retrieve subject, sender, date, and attachment filenames.
4. Print a summary for each email.

## Output

For each of the (up to 3) matching emails, print to stdout:

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date>
    Attachments: <filename1>, <filename2>, …
```

If fewer than 3 matches exist, print however many were found. If none, print `No matching emails with attachments found.`

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

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to the Google Cloud Console.
- API errors: surface the error message and exit with a non-zero code.
- No results: handled gracefully (see Output section).

## Out of Scope

- Downloading attachment content.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts simultaneously.
