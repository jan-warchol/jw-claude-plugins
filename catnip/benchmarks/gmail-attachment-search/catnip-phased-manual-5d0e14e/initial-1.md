# Gmail Attachment Search Script

## Overview

A command-line Python script that searches the user's Gmail inbox using a provided query string and returns the three most recent matching emails that contain attachments.

## Inputs

- A search query string passed as a command-line argument (e.g., `"from:boss subject:report"`), using Gmail's standard search syntax.

## Behavior

1. Authenticate with the Gmail API using OAuth 2.0, storing credentials locally for reuse across runs.
2. Search Gmail using the provided query, combining it with `has:attachment` to filter for emails with attachments only.
3. Retrieve results sorted by date descending and return the three most recent matches.
4. If fewer than three matching emails exist, return all that are found.
5. If no matching emails are found, print a clear message and exit with a non-zero status code.

## Output

For each matching email, print to stdout:

- Date received
- Sender (`From` header)
- Subject line
- List of attachment filenames

Output is human-readable, formatted as plain text. One blank line separates each email's block.

## Authentication

- Uses the Gmail API via `google-auth` and `google-api-python-client`.
- OAuth credentials are loaded from a `credentials.json` file in the working directory.
- The token is cached in `token.json` to avoid re-authentication on subsequent runs.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Error Handling

- Missing `credentials.json`: print an actionable error message explaining how to obtain credentials from Google Cloud Console.
- API errors: print the error message and exit with a non-zero status code.
- No query argument provided: print usage instructions and exit with a non-zero status code.

## Constraints

- Single-file script (`gmail_search.py`), no project scaffolding.
- No external dependencies beyond `google-auth-oauthlib`, `google-auth-httplib2`, and `google-api-python-client`.
- Read-only Gmail access; the script does not modify, delete, or send any emails.
