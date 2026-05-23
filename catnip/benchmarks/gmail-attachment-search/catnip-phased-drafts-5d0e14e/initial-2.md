# Gmail Attachment Search Script — Spec

## Overview

A Python CLI script that accepts a Gmail search query from the user, searches their Gmail inbox, and returns the 3 most recent matching emails that contain attachments.

## Functional Requirements

- Accept a search query string as a command-line argument (e.g. `python search_gmail.py "from:boss@example.com"`)
- Authenticate with Gmail using OAuth 2.0 (Google API credentials)
- Search Gmail using the provided query, additionally filtering for messages with attachments
- Return the 3 most recent matching emails that have at least one attachment
- For each matching email, display:
  - Date received
  - Sender (`From` header)
  - Subject
  - List of attachment filenames and their MIME types

## Authentication

- Use Google OAuth 2.0 with the Gmail API (`gmail.readonly` scope)
- Store OAuth tokens in a local file (`token.json`) so re-authentication is not required on every run
- On first run, open a browser window to complete the OAuth flow
- Credentials file (`credentials.json`) must be present in the working directory (obtained from Google Cloud Console)

## Input

- Single required positional argument: the Gmail search query string
- The query follows Gmail search syntax (e.g. `"invoice"`, `"from:alice subject:report"`)
- The script appends `has:attachment` to the user's query automatically so only emails with attachments are returned

## Output

- Print results to stdout, human-readable
- Show a header indicating the query used
- For each of the (up to) 3 results, show a numbered entry with date, sender, subject, and attachment list
- If fewer than 3 matching emails exist, return however many are found
- If no matching emails are found, print a clear "no results" message and exit with code 0

## Error Handling

- Missing `credentials.json`: print a clear error message explaining where to obtain it, exit with code 1
- Gmail API errors (network, quota, auth failure): print the error and exit with code 1
- Invalid or empty query string: print usage and exit with code 1

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` (Google API client libraries)
- Python 3.8+

## Out of Scope

- Downloading attachment files
- Modifying, deleting, or sending emails
- Pagination beyond the first page of results (the API default of 100 results is sufficient to find 3 matches)
- GUI or web interface
