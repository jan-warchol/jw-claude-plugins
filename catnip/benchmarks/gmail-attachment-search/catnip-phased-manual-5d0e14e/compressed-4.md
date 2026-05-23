# Gmail Attachment Search Script

## Overview

Python CLI script: authenticates with Gmail, searches messages matching a
user-provided query, and prints metadata for the 3 most recent with attachments.

## Inputs

- **Search query**: CLI argument (e.g. `"from:boss@company.com"` or `"invoice"`).

## Behavior

1. Authenticate via OAuth 2.0 (read-only scope).
2. Append `has:attachment` to the query unless already present.
3. Search at message level (not thread); retrieve the 3 most recent by
   `internalDate` descending.

## Output

Per message, print to stdout:

- Date/time received
- Sender (`From` header)
- Subject
- Attachment filenames and MIME types

Separate messages with a blank line. Only `Content-Disposition: attachment`
parts are listed (inline images excluded).

## Authentication

- Gmail API via `google-auth` and `google-api-python-client`.
- OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Token stored in `token.json`; refreshed automatically when expired.
- `credentials.json` (from Google Cloud Console) must be present; Gmail API
  must already be enabled in the user's project.

## Error handling

- Fewer than 3 matches: print what's found.
- Zero matches: print "no results", exit 1.
- Missing `credentials.json`: print actionable message.
- API errors: surface the error, exit non-zero; no retries.

## Explicit exclusions

- Attachments are not downloaded.
- No pagination (always at most 3 results).
- No filtering by attachment type, size, or filename.

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`
