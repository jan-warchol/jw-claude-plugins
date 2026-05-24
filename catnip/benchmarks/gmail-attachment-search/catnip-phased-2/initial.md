# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, accepts a search query from the user, and prints details of the most recent 3 emails matching that query that contain at least one attachment.

---

## Inputs

- **Search query** — a string passed as a CLI argument (e.g. `"from:boss subject:report"`). The script appends `has:attachment` to the query automatically so only emails with attachments are returned.

---

## Authentication

- Uses the Gmail API via `google-auth` + `google-api-python-client`.
- Credentials stored in `credentials.json` (OAuth 2.0 client secret, downloaded from Google Cloud Console).
- On first run, opens a browser for the OAuth consent flow and saves the resulting token to `token.json`.
- On subsequent runs, loads the token from `token.json` and refreshes it if expired.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.

---

## Core Logic

1. Parse the CLI argument for the search query.
2. Append `has:attachment` to the query string.
3. Call `users.messages.list` with `maxResults=3` and the composed query.
4. For each returned message ID, call `users.messages.get` with `format=metadata` and `metadataHeaders=["From", "Subject", "Date"]`.
5. Collect attachment names by inspecting the `parts` of the message payload for parts where `filename` is non-empty.
6. Print a summary for each email.

---

## Output

For each of the (up to 3) matching emails, print:

```
[1] Date: <date>
    From: <sender>
    Subject: <subject>
    Attachments: <filename1>, <filename2>, ...
```

If no matching emails are found, print:

```
No emails with attachments found for query: "<query>"
```

---

## Error Handling

- Missing `credentials.json`: print a clear error message explaining how to obtain it.
- Gmail API errors: surface the error message and exit with a non-zero code.
- No results: handled by the "no emails found" message above.

---

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

---

## File Layout

```
gmail_search_attachments.py   # main script
credentials.json              # OAuth client secret (user-provided, not committed)
token.json                    # saved token (auto-generated, not committed)
requirements.txt              # pip dependencies
```
