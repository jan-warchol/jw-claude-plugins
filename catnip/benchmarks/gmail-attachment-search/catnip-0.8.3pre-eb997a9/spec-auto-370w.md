# Spec: Gmail attachment-search script

## Goal

A simple Python CLI script that searches Gmail with a user-supplied query and returns the 3 most
recent matching emails that carry attachments. Lets a user quickly locate recent
attachment-bearing mail without opening Gmail.

## Requirements

- Accept a Gmail search query as a command-line argument.
- Restrict results to mail with attachments by appending `has:attachment` to the query
  (server-side filtering).
- Return the 3 most recent matches (Gmail's search order is already newest-first; take the top 3).
  Return fewer if fewer match.
- For each result, print to stdout: sender, date, subject, and attachment filenames.
- No files are written; attachments are not downloaded.
- Exit cleanly with a clear message when there are zero matches.

### Out of scope

- Downloading or saving attachments.
- Interactive query prompts, pagination, or result counts other than 3.
- Filtering out inline images (relying on Gmail's `has:attachment` is acceptable).

## Design

- **API**: Gmail REST API via `google-api-python-client`, scope `gmail.readonly`.
- **Auth**: OAuth2 installed-app flow (`google-auth-oauthlib`). Read client secrets from
  `credentials.json`; cache/refresh the user token in `token.json`. Trigger the browser consent
  flow only when no valid cached token exists.
- **Flow**:
  1. `users.messages.list` with `q = "<user query> has:attachment"`, `maxResults=3`.
  2. For each returned id, `users.messages.get` with `format=metadata` (headers `From`, `Date`,
     `Subject`) to read metadata, and walk the payload parts for parts with a non-empty `filename`
     to collect attachment names.
  3. Print formatted output.
- **Trade-off**: `maxResults=3` keeps it minimal and avoids client-side re-sorting, accepting that
  any non-recency quirks in Gmail ordering are inherited as-is.

## Unknowns

### Assumptions

- The user has a Google Cloud project with the Gmail API enabled and a downloaded
  `credentials.json`; supplying it is the user's responsibility.
- A desktop/browser environment is available for the one-time OAuth consent.
- Gmail's `has:attachment` semantics match the user's notion of "has attachments" (it includes
  inline content).
- `messages.list` returns matches newest-first, so the first 3 ids are the 3 most recent.

### Risks / open questions

- Missing or invalid credentials, expired/revoked tokens, and API rate limits are surfaced as
  errors but not specially handled.
- Empty or malformed queries are passed through to Gmail as-is.
