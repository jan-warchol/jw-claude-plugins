# Gmail Attachment Search — Spec

## 1. Purpose

A CLI Python script that accepts a Gmail search query and prints metadata for the 3 most recent
matching emails that contain attachments.

## 2. Requirements

- Accept a search query string as a CLI argument (e.g. `"from:boss subject:report"`)
- Authenticate to Gmail via OAuth2 using a `credentials.json` file
- Find the 3 most recent emails (by received date) matching the query that have at least one
  attachment
- For each match, print: subject, sender, received date, and attachment filenames
- Do not download attachments
- If fewer than 3 qualifying emails exist, print what was found with a note
- Exit with a clear error message on auth failure or API error

**Out of scope:** downloading files, modifying/labeling emails, non-Gmail providers, pagination
UI, multi-account support.

## 3. Design

**Dependencies:** `google-api-python-client`, `google-auth-oauthlib`

**Auth flow:**

- Read `credentials.json` from the working directory (obtained from Google Cloud Console)
- Cache the OAuth token in `token.json`; browser-based consent prompt on first run
- Scope: `https://www.googleapis.com/auth/gmail.readonly`

**Search logic:**

1. Call `users.messages.list` with the user's query, `maxResults=50`, ordered newest-first
   (default)
2. For each message ID, call `users.messages.get` with `format=metadata` to read headers and MIME
   parts
3. Detect attachments by checking payload parts for a non-empty `filename` with
   `Content-Disposition: attachment`
4. Collect the first 3 qualifying messages; paginate (up to 2 pages) if needed to find them

**Output:** plain-text blocks, one per email, printed to stdout.

## 4. Uncertainty

- **Inline images:** Parts with a filename but `Content-Disposition: inline` are excluded from the
  attachment count; this may miss some edge cases
- **Large result sets:** Capping at 2 pages (~100 messages) keeps latency acceptable but could
  miss results in very large mailboxes
- **Token expiry:** Relies on `google-auth-oauthlib` to refresh tokens transparently; behavior on
  revoked access is not explicitly handled
