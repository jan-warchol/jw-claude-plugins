# Gmail Attachment Search Script

## Overview

A command-line Python script that searches Gmail for emails matching a user-provided query and returns the 3 most recent matching emails that contain attachments.

## Functional Requirements

- Accept a search query string as a command-line argument.
- Authenticate with the Gmail API using OAuth 2.0.
- Search Gmail using the provided query, filtered to only include emails that have attachments.
- Return the 3 most recent matching emails.
- For each result, display:
  - Email subject
  - Sender
  - Date received
  - List of attachment filenames

## Authentication

- Use OAuth 2.0 with a `credentials.json` file (downloaded from Google Cloud Console).
- Store the OAuth token in a local `token.json` file for reuse across runs.
- Prompt the user to authorize via browser on first run.

## Non-Functional Requirements

- Script is a single Python file with no custom modules.
- Dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.
- Clear error message if no matching emails are found.
- Clear error message if authentication fails.

## Out of Scope

- Downloading attachment files.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts.
