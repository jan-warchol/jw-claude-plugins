# Spec: Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with the Gmail API, searches a user's inbox using a query string provided at runtime, and prints a summary of the three most recent matching emails that contain at least one attachment.

## Functional Requirements

### Input
- The script accepts a single positional argument: the Gmail search query string (e.g., `"from:boss@example.com subject:report"`).
- Standard Gmail search operators must be supported as-is (the query is passed directly to the API).

### Processing
1. Authenticate with the Gmail API using OAuth 2.0.
2. Search the user's mailbox with the provided query, filtering to messages that have attachments.
3. Sort results by date descending and select the three most recent.
4. For each selected email, retrieve the full message to extract metadata.

### Output
For each of the (up to) three matched emails, print:
- Sender (`From`)
- Subject
- Date
- A list of attachment filenames and their MIME types

If fewer than three emails match, print however many were found. If none match, print an informative message.

## Authentication

- Use the `google-auth` and `google-auth-oauthlib` libraries.
- The OAuth client credentials are read from a `credentials.json` file in the working directory (downloaded from Google Cloud Console).
- On first run the browser opens for the OAuth consent flow; the resulting token is cached in `token.json` so subsequent runs are non-interactive.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Dependencies

| Package | Purpose |
|---|---|
| `google-api-python-client` | Gmail REST API wrapper |
| `google-auth-oauthlib` | OAuth 2.0 flow |
| `google-auth-httplib2` | HTTP transport for auth |

Install via: `pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

## Error Handling

- Missing `credentials.json`: print a clear error with setup instructions and exit with code 1.
- No search query provided: print usage and exit with code 1.
- API errors (network, quota, permission): print the error message and exit with code 1.

## Non-Goals

- Downloading attachment content (only metadata is shown).
- Sending or modifying emails.
- Pagination beyond the first page of results (the API returns up to 500 results per call; for this use case that is sufficient).
- A GUI or web interface.
