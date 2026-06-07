# Gmail Attachment Search Script

## Goal

CLI tool to search a Gmail inbox by user-provided query and display metadata for the 3 most recent
matching emails that have attachments.

## Requirements

- Accept a Gmail search query string as a CLI argument
- Authenticate with Gmail via OAuth2; cache token locally after first login
- Return the 3 most recent emails matching the query that have at least one attachment
- Output per email: subject, sender, date, and attachment filenames
- Do not download attachment content
- Exit with a clear error message if fewer than 3 matching emails exist

Out of scope: attachment download, pagination beyond the top 3, non-Gmail providers.

## Solution

- Use `google-api-python-client` and `google-auth-oauthlib`
- Append `has:attachment` to the user's query before calling `messages.list`, exploiting Gmail's
  native operator support
- Fetch full message payload (`format=full`) for each result to extract part metadata without
  downloading bodies
- Detect attachments by checking message parts for non-empty `filename` fields
- OAuth credentials loaded from `credentials.json` (obtained from Google Cloud Console); token
  persisted to `token.json`
- Single-file script with no internal modules; dependencies declared as a comment at the top

## Unknowns

- `credentials.json` must be pre-provisioned by the user; script will fail clearly if absent
- Gmail's `messages.list` returns up to 100 results per page; fetching only the first page is
  sufficient given the 3-result limit
- Attachment detection via `filename` field may miss inline attachments with
  `Content-Disposition: inline` but no filename
