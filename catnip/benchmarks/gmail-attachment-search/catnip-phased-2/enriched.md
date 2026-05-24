# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, accepts a search query from the user, and prints details of the most recent 3 emails matching that query that contain at least one attachment. "Most recent" is defined by Gmail's default message ordering (newest first), which is what `users.messages.list` returns by default.

---

## Inputs

- **Search query** — a string passed as a CLI argument (e.g. `"from:boss subject:report"`). The script silently appends `has:attachment` to the query so that only emails with attachments are returned, without requiring the user to include it manually.

---

## Authentication

- Uses the Gmail API via `google-auth` + `google-api-python-client`.
- Credentials stored in `credentials.json` (OAuth 2.0 client secret, downloaded from Google Cloud Console).
- On first run, opens a browser for the OAuth consent flow and saves the resulting token to `token.json`.
- On subsequent runs, loads the token from `token.json` and refreshes it if expired.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- **Why OAuth over App Passwords**: App Passwords require 2FA and a Google Workspace account; OAuth works for all Gmail accounts and follows the recommended API path.

---

## Core Logic

1. Parse the CLI argument for the search query.
2. Compose the final query: `<user_query> has:attachment`.
3. Call `users.messages.list` with `maxResults=3` and the composed query. Results are newest-first by default.
4. For each returned message ID, call `users.messages.get` with `format=full` to retrieve the full MIME payload including all parts.
5. Extract attachment filenames by recursively walking the `parts` tree, collecting any part where `filename` is non-empty. Inline parts with no filename are skipped.
6. Print a summary for each email.

**Note on `format=full`**: `format=metadata` does not return message parts and cannot be used to list attachments. `format=full` is required.

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

## Explicit Exclusions

- Attachment content is not downloaded; only filenames are reported.
- Only a single Gmail account (the one authenticated) is supported.
- No interactive query builder; the query must be passed as a CLI argument.

---

## Error Handling

- Missing `credentials.json`: print a clear error message explaining how to obtain it.
- Gmail API errors: surface the error message and exit with a non-zero code.
- No results: handled by the "no emails found" message above.

---

## Assumptions and Risks

- **Ordering**: relies on Gmail API's default newest-first ordering; no explicit `orderBy` parameter exists in the messages API, so this is an implicit guarantee.
- **Nested MIME**: multipart messages may nest `multipart/mixed` inside `multipart/alternative`; the recursive walk handles arbitrary depth.
- **`has:attachment` append**: if the user already includes `has:attachment` in their query, appending it again is harmless (Gmail deduplicates the filter).

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
