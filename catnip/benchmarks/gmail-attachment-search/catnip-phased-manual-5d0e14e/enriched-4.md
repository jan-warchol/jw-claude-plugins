# Gmail Attachment Search Script

## Overview

A Python command-line script that authenticates with Gmail, searches for emails
matching a user-provided query, and prints metadata for the 3 most recent
results that contain file attachments.

## Inputs

- **Search query**: a string provided as a command-line argument (e.g.
  `"from:boss@company.com"` or `"invoice"`).

## Behavior

1. Authenticate with the user's Gmail account using OAuth 2.0 (read-only scope).
2. Build the effective query by appending `has:attachment` unless the user's
   query already includes it.
3. Search at the **message level** (not thread level) and retrieve the 3 most
   recent messages, ordered by `internalDate` descending.
4. For each message, fetch headers and MIME part metadata to identify
   attachments.

## Output

For each of the (up to) 3 messages, print to stdout in a human-readable block:

- Date and time received (local timezone)
- Sender (`From` header)
- Subject line
- List of attachment filenames and MIME types

Messages are separated by a blank line. Inline images
(`Content-Disposition: inline`) are excluded; only `Content-Disposition:
attachment` parts are listed. Output is plain text — no JSON or
machine-readable format.

## Authentication

- Use the Gmail API via `google-auth` and `google-api-python-client`.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Store the token in `token.json` in the working directory; refresh
  automatically when expired.
- A `credentials.json` (downloaded from Google Cloud Console) must be present.
  The script assumes the Gmail API is already enabled in the user's Google
  Cloud project — setup instructions are out of scope.

## Error handling

- Fewer than 3 matches: print however many are found.
- Zero matches: print a clear "no results" message and exit with status code 1.
- Missing `credentials.json`: print an actionable message explaining where to
  obtain it.
- API errors (auth failure, quota exceeded): surface the error and exit
  non-zero; no retry logic.

## Explicit exclusions

- Attachments are not downloaded or saved.
- Only a single Gmail account is supported per run.
- No filtering by attachment type, size, or filename.
- No pagination: at most 3 results are returned regardless of total match count.

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`
