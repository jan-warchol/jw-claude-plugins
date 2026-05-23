# Gmail Attachment Search Script

## Overview

A command-line Python script that accepts a Gmail search query, searches the user's Gmail inbox, and returns the three most recent matching emails that contain attachments.

## Functional Requirements

- Accept a search query string as a command-line argument
- Authenticate with Gmail using OAuth 2.0
- Search Gmail for emails matching the query, filtered to only those with attachments
- Return up to 3 most recent matching results
- For each result, display:
  - Sender (From header)
  - Subject line
  - Date received
  - List of attachment filenames

## Authentication

- Use Google OAuth 2.0 with the Gmail API (read-only scope)
- Store credentials in a local file (e.g. `token.json`) so re-authentication is not required on subsequent runs
- On first run, open a browser window for the user to authorize access

## Input

- Single positional CLI argument: the Gmail search query string (same syntax as the Gmail search box)
- Example: `python search_gmail.py "invoice from:accounting@example.com"`

## Output

- Plain-text output to stdout
- One block per email, showing sender, subject, date, and attachment names
- If fewer than 3 matching emails exist, return however many are found
- If no matching emails are found, print an informative message

## Error Handling

- Invalid or expired credentials: prompt re-authentication
- Network errors: print a clear error message and exit with non-zero status
- Gmail API quota exceeded: print a clear error message and exit with non-zero status

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Out of Scope

- Downloading attachment content
- Modifying or deleting emails
- Pagination beyond the first page of results (fetching more than Gmail API returns in a single call is not required)
- GUI or interactive interface
