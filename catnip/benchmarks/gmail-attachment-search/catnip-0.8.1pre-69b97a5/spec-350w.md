# Gmail Attachment Search Script — Spec

## Purpose

A command-line Python script that accepts a Gmail search query from the user, searches their inbox
via the Gmail API, and prints metadata for the three most recent matching emails that contain
attachments.

---

## Requirements

- Accepts a single positional CLI argument: the Gmail search query string (same syntax as the
  Gmail search box).
- Searches the authenticated user's Gmail account and filters results to emails that have at least
  one attachment.
- Returns exactly the 3 most recent such emails (by date); fewer if fewer than 3 exist.
- For each result, prints to stdout:
  - Subject
  - Sender (`From` header)
  - Date
  - Attachment filenames (one per line, indented)
- Prints a clear message if no matching emails with attachments are found.
- Does not download, save, or modify any emails or attachments.
- Exits with a non-zero code on authentication or API errors, with a human-readable error message.

---

## Design

**Authentication:** OAuth2 via a `credentials.json` file (downloaded from Google Cloud Console).
On first run the script opens a browser for the OAuth consent flow and caches a `token.json`
locally for subsequent runs.

**Library:** `google-api-python-client` + `google-auth-oauthlib`. These are the standard
Google-maintained libraries and cover the full OAuth + API surface needed.

**Search flow:**

1. Call `users.messages.list` with the user-supplied query. Gmail's query syntax natively supports
   operators like `has:attachment`, but to keep logic simple the script fetches up to ~20 results
   and filters client-side for `parts` containing non-inline attachments.
2. Sort by `internalDate` descending, take the first 3.
3. Fetch full message headers + part metadata (no body or attachment data) via
   `users.messages.get` with `format=metadata`.

**Scope required:** `https://www.googleapis.com/auth/gmail.readonly`.

---

## Uncertainty

- **Quota:** `messages.list` + up to 20 `messages.get` calls per run; well within default Gmail
  API quotas.
- **Inline images:** Parts with `Content-Disposition: inline` are excluded from the attachment
  list; only `attachment` disposition is counted.
- **Query amplification:** If the user's query already includes `has:attachment`, the client-side
  filter is redundant but harmless.
- **Token refresh:** `google-auth-oauthlib` handles token expiry automatically; no special
  handling needed.
