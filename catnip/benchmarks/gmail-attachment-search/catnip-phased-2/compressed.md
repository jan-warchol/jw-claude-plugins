# Gmail Attachment Search Script — Spec

## Overview

CLI Python script that authenticates with Gmail via OAuth 2.0, accepts a search query, and prints the 3 most recent matching emails that have attachments. Order is newest-first, Gmail API's default for `users.messages.list`.

---

## Inputs

- **Search query** — CLI argument (e.g. `"from:boss subject:report"`). The script silently appends `has:attachment`; if the user includes it too, Gmail deduplicates it harmlessly.

---

## Authentication

- Gmail API via `google-auth` + `google-api-python-client`; scope: `gmail.readonly`.
- `credentials.json`: OAuth 2.0 client secret (from Google Cloud Console).
- First run: browser OAuth flow; token saved to `token.json`. Subsequent runs: load and auto-refresh.
- OAuth chosen over App Passwords because App Passwords require 2FA + Workspace; OAuth works for all Gmail accounts.

---

## Core Logic

1. Compose query: `<user_query> has:attachment`.
2. `users.messages.list(maxResults=3, q=<query>)` — newest-first by default.
3. For each message ID: `users.messages.get(format=full)` to retrieve the full MIME payload. (`format=metadata` cannot be used — it omits message parts.)
4. Recursively walk the `parts` tree; collect filenames where `filename` is non-empty; skip inline parts.
5. Print summary for each email.

---

## Output

```
[1] Date: <date>
    From: <sender>
    Subject: <subject>
    Attachments: <filename1>, <filename2>, ...
```

No results: `No emails with attachments found for query: "<query>"`

---

## Exclusions

- Attachment content is not downloaded — filenames only.
- Single account only; no interactive query builder.

---

## Error Handling

- Missing `credentials.json`: explain how to obtain it and exit.
- Gmail API error: print message, exit non-zero.

---

## Assumptions

- Newest-first ordering is implicit (no `orderBy` in the messages API).
- Recursive MIME walk handles arbitrary nesting depth.

---

## Dependencies & Files

```
google-api-python-client, google-auth-httplib2, google-auth-oauthlib

gmail_search_attachments.py   # main script
credentials.json              # not committed
token.json                    # not committed
requirements.txt
```
