# Gmail Attachment Search Script

## Overview

A Python command-line script that authenticates with Gmail, searches for emails
matching a user-provided query, and returns the most recent 3 results that
contain attachments.

## Inputs

- **Search query**: a string provided as a command-line argument (e.g.
  `"from:boss@company.com"` or `"invoice"`).

## Behavior

1. Authenticate with the user's Gmail account using OAuth 2.0.
2. Search Gmail for threads/messages matching the query, filtered to only those
   that have at least one attachment (`has:attachment` is appended to the
   query automatically).
3. Return the 3 most recent matching messages.

## Output

For each of the (up to) 3 messages, print to stdout:

- Date and time received
- Sender (`From` header)
- Subject line
- List of attachment filenames and their MIME types

## Authentication

- Use the Gmail API via the `google-auth` and `google-api-python-client`
  libraries.
- Store OAuth credentials in a local file (`token.json`) so the user only
  needs to authorize once.
- A `credentials.json` file (downloaded from Google Cloud Console) must be
  present in the working directory.

## Error handling

- If fewer than 3 matching messages exist, print however many are found.
- If no messages match, print a clear "no results" message and exit with a
  non-zero status code.
- If authentication fails, print an actionable error message.

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`
