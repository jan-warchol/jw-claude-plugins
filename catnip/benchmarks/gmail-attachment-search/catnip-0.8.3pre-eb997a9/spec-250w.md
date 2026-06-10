# Specification: Gmail Attachment Search Script

## Goal

Provide a simple Python script that searches a user's Gmail for messages matching a user-supplied
query and reports the 3 most recent matches that have attachments.

## Requirements

- Accept the search query as a command-line argument; the query uses native Gmail search syntax
  (e.g. `from:boss invoice`).
- Restrict results to messages with attachments and return the 3 most recent such matches, newest
  first.
- For each result, print to the console: sender, subject, date, and attachment filename(s).
- Out of scope: downloading attachment files, sending/modifying mail, GUI, pagination beyond the 3
  results, non-Gmail providers.
- Success: given valid credentials and a query, the script prints up to 3 correctly ordered
  entries with accurate metadata. Fewer than 3 matches prints all available; zero matches prints a
  clear "no results" message.

## Design

- Use `google-api-python-client` with OAuth 2.0 desktop flow. On first run the user consents via
  browser; a `token.json` caches the refresh token, `credentials.json` holds the client config.
  Scope: `gmail.readonly`.
- Append `has:attachment` to the user query so attachment filtering happens server-side; rely on
  Gmail's default newest-first ordering and take the first 3 ids.
- Fetch each message with `format=metadata` (plus part filenames) to read headers and attachment
  names without downloading payloads.
- Handle missing credentials and API/auth errors with a readable message and non-zero exit.

## Unknowns

- Assumes the user can create a Google Cloud project and download `credentials.json`.
- Assumes "last 3" means most recent by date.
- Open: behavior for inline images that are technically attachments.
