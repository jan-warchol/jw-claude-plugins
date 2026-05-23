# Gmail Attachment Search Script

## Overview

A command-line Python script that accepts a Gmail search query, searches the user's Gmail inbox for emails that have attachments, and prints details of the three most recent matching results. "Most recent" means ordered by date descending as returned by the Gmail API.

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

- Use Google OAuth 2.0 with the Gmail API (read-only scope: `gmail.readonly`)
- The user must supply a `credentials.json` file (OAuth client secret downloaded from Google Cloud Console). The script reads it from the working directory by default.
- Store the resulting access token in `token.json` so re-authentication is not required on subsequent runs
- On first run, open a browser window for the user to authorize access; if no browser is available, print the authorization URL for manual use

## Input

- Single positional CLI argument: the Gmail search query string (same syntax as the Gmail search box)
- Example: `python search_gmail.py "invoice from:accounting@example.com"`
- The script appends `has:attachment` to the user's query server-side, so the user does not need to include it

## Output

Plain-text to stdout, one block per email separated by a blank line:

```
From: Alice <alice@example.com>
Subject: Q1 Invoice
Date: 2026-04-15
Attachments: invoice_q1.pdf, terms.docx
```

- If fewer than 3 matching emails exist, print however many are found
- If none are found, print: `No matching emails with attachments found.`

## Design Choices

- **Gmail API over IMAP**: the Gmail API supports the full Gmail search syntax server-side and returns results already sorted by relevance/date, eliminating the need to fetch and filter messages locally.
- **Server-side attachment filter**: appending `has:attachment` to the query and letting the API filter is simpler and faster than fetching all matches and inspecting MIME parts client-side. Inline images (Content-Disposition: inline) are excluded by this filter; only proper file attachments are matched.
- **Single API page**: Gmail API default `maxResults` is 100, so fetching one page is sufficient to get 3 results without pagination logic.

## Error Handling

- Missing `credentials.json`: print a setup instruction message and exit with non-zero status
- Invalid or expired token: delete `token.json` and prompt re-authentication automatically
- Network errors: print a clear error message and exit with non-zero status
- Gmail API quota exceeded: print a clear error message and exit with non-zero status

## Assumptions and Open Questions

- The user has created a Google Cloud project with the Gmail API enabled and downloaded `credentials.json`. No setup automation is in scope.
- Open question: if an email has only inline images (e.g., embedded logos), it will not appear in results. This is the intended behavior, but could be revisited if the user wants inline images treated as attachments.

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Out of Scope

- Downloading attachment content
- Modifying or deleting emails
- Pagination beyond the first API page
- GUI or interactive interface
