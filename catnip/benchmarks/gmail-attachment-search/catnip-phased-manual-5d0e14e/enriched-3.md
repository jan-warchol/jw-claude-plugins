# Gmail Attachment Search Script

## Overview

A single-file command-line Python script that searches Gmail for emails matching a user-provided query and prints the 3 most recent matching emails that contain attachments, with metadata and attachment filenames.

## Functional Requirements

- Accept a search query string as a command-line argument (e.g., `python script.py "from:boss"`).
- Authenticate with the Gmail API using OAuth 2.0.
- Automatically append `has:attachment` to the user's query before sending it to the API, so the user does not need to include it manually.
- Sort results by date descending and take the first 3.
- If fewer than 3 matching emails exist, display however many are found without error.
- For each result, print to stdout:
  - Email subject (fallback: `"(no subject)"`)
  - Sender address
  - Date received (human-readable, e.g., `2024-03-15`)
  - Filenames of all non-inline attachments (i.e., parts with `Content-Disposition: attachment`)
- If no matching emails are found, print a clear message and exit with code 0.

## Authentication

- Use OAuth 2.0 with a `credentials.json` file (downloaded from Google Cloud Console).
- Request the `https://www.googleapis.com/auth/gmail.readonly` scope.
- Store the OAuth token in a local `token.json` file for reuse across runs.
- Prompt the user to authorize via browser on first run; refresh the token automatically on subsequent runs if expired.

### Assumptions and prerequisites

- The user has a Google Cloud project with the Gmail API enabled and `credentials.json` available in the working directory.
- The script targets the authenticated user's primary Gmail inbox; Trash and Spam are excluded by default (Gmail API default behavior).

## Non-Functional Requirements

- Script is a single Python file with no custom modules.
- Dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.
- Print a clear error message if authentication fails and exit with a non-zero code.

## Design Decisions

- **`has:attachment` appended automatically**: Simplifies the user interface; the script's purpose is explicitly attachment search, so adding the filter silently is appropriate.
- **OAuth 2.0 over service account**: Service accounts require domain-wide delegation, which is unavailable for personal Gmail accounts. OAuth 2.0 is the standard approach for user-owned mailboxes.
- **Inline images excluded**: MIME parts with `Content-Disposition: inline` are skipped; only parts with `Content-Disposition: attachment` are reported, matching user expectations.

## Out of Scope

- Downloading or saving attachment files.
- Pagination beyond the first page of API results.
- Support for multiple Gmail accounts.
- Configurable result count (always 3).
