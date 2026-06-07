# Gmail Attachment Search Script

## Goal

A CLI Python script that accepts a Gmail search query and prints metadata for the 3 most recent
matching emails that have at least one attachment.

## Requirements

- Accept a Gmail search query string as a CLI argument.
- Query Gmail and filter results to emails with attachments.
- Return the **3 most recent** such emails (or fewer if fewer match).
- For each matching email, print to stdout:
  - Subject, sender, date
  - Attachment name(s) and size(s)
- Exit with a non-zero code and a clear error message on failure (auth error, no matches, API
  error).
- Out of scope: downloading attachments, pagination beyond finding 3 results, modifying emails.

## Design

- **Auth**: OAuth2 via `google-auth-oauthlib` + Gmail API (`googleapis`). On first run, opens
  browser for consent and caches token in `token.json`. Requires `credentials.json` (OAuth client
  secret from Google Cloud Console) in the working directory.
- **API usage**: Use `users.messages.list` with the user's query plus `has:attachment` appended
  (or ANDed), then `users.messages.get` (with `format=metadata`, fetching `payload.parts`) for
  each candidate until 3 with attachments are confirmed. Fetch only as many messages as needed.
- **Attachment detection**: A message has an attachment if any `payload.parts` entry has a
  non-empty `filename` and a `body.attachmentId` (or non-zero `body.size`).
- **Output format**: Human-readable plain text; one block per email separated by blank lines.
- **Dependencies**: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Unknowns

- **Assumption**: `has:attachment` in the Gmail query is sufficient and accurate; no secondary
  filtering beyond confirming attachment metadata is needed.
- **Assumption**: `credentials.json` is provided by the user; the script does not handle GCP
  project setup.
- **Risk**: Gmail API rate limits could be hit if the query returns many non-attachment results
  before finding 3 matches; not handled beyond surfacing the API error.
- **Open question**: Whether `token.json` path should be configurable — assumed fixed for
  simplicity.
