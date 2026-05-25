# Gmail Attachment Search Script — Spec

## Overview

Python CLI that accepts a Gmail search query and returns the 3 most recent matching emails containing attachments.

## Functional Requirements

- `python search_gmail.py "<query>"` — single required positional argument (Gmail search syntax)
- Appends `has:attachment` to the query automatically
- Returns up to 3 most recent matching emails
- For each result, display: date received, sender, subject, attachment filenames and MIME types
- "Attachment" = `Content-Disposition: attachment`; inline/embedded content excluded

## Authentication

- Google OAuth 2.0, `gmail.readonly` scope
- `credentials.json` must be in the working directory (from Google Cloud Console)
- Tokens cached in `token.json`; browser flow on first run

## Output

- Human-readable stdout; header showing the query used
- Numbered entries: date (local time, e.g. `2024-03-15 09:42`), sender, subject, attachments indented as `filename (MIME type)`
- No results → clear message, exit 0

## Error Handling

All errors exit with code 1:
- Missing `credentials.json`: explain where to obtain it
- Gmail API errors (network, quota, auth): print the error
- Invalid or empty query: print usage

## Assumptions and Risks

- User must have a Google Cloud project with Gmail API enabled and OAuth credentials configured
- `token.json` is plaintext; protect from unauthorized access and version control

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- Python 3.8+

## Out of Scope

Downloading attachments, writing/sending emails, pagination beyond the API default, GUI.
