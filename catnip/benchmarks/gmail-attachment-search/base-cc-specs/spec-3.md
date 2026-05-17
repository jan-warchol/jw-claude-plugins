# Spec: Gmail Attachment Search Script

## Overview

A Python command-line script that accepts a search query, searches the user's Gmail inbox, and
returns the 3 most recent matching emails that contain attachments.

## Inputs

- `query` (string, required): A Gmail search query string provided by the user (e.g.
  `"from:boss@company.com"`, `"subject:invoice"`). Passed as a CLI argument or prompted
  interactively.

## Outputs

For each of the up to 3 matching emails (most recent first), print to stdout:

- Date received
- Sender (`From` header)
- Subject
- List of attachment filenames with their MIME types

## Behavior

1. Authenticate with Gmail using OAuth 2.0 (credentials stored locally; prompt the user to authorize
   on first run).
2. Issue a Gmail search combining the user's query with `has:attachment` to filter for emails with
   attachments.
3. Retrieve results sorted by date descending; take the first 3.
4. For each result, fetch the full message and extract attachment metadata (filename, MIME type). Do
   not download attachment content.
5. Print results in a human-readable format. If fewer than 3 matches exist, print however many are
   found. If none exist, print a clear "no results" message and exit with code 0.

## Error Handling

- Missing or invalid credentials: print a descriptive error and exit with code 1.
- Gmail API errors (rate limit, network failure): print the error message and exit with code 1.
- Invalid query syntax accepted by the Gmail API as-is; any API-reported query error surfaces to the
  user verbatim.

## Implementation Constraints

- Language: Python 3.9+
- Gmail access: `google-api-python-client` + `google-auth-oauthlib` (Gmail API v1).
- OAuth scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only, minimum privilege).
- Credentials file: `credentials.json` in the working directory (standard Google Cloud OAuth 2.0
  client secret file); token cached in `token.json`.
- No external dependencies beyond the two Google libraries above and their transitive deps.
- Single-file script (`gmail_attachment_search.py`); no package structure required.

## Non-Goals

- Downloading or saving attachment content.
- Sending, modifying, or deleting emails.
- Pagination beyond the first 3 results.
- Support for multiple Gmail accounts simultaneously.
