# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail, searches for emails
matching a user-provided query, and returns the last 3 matching emails that
contain attachments.

---

## Functional Requirements

### Input
- The script accepts a single positional argument: a Gmail search query string
  (e.g. `"from:boss@company.com"`, `"subject:invoice"`, `"label:important"`).
- The query syntax follows Gmail's standard search operators.

### Processing
- Authenticate with the Gmail API using OAuth 2.0.
- Search the user's Gmail inbox using the provided query, additionally
  filtering for messages that have attachments (`has:attachment`).
- Retrieve the most recent 3 messages matching the combined query.

### Output
For each of the (up to) 3 emails, print to stdout:
- Date sent
- Sender (`From:` header)
- Subject
- A list of attachment filenames

---

## Authentication

- Use OAuth 2.0 with the Gmail API (read-only scope: `gmail.readonly`).
- Store credentials in a local file (`token.json`) so the user only needs to
  authorize once via browser.
- Expect a `credentials.json` file (downloaded from Google Cloud Console) in
  the working directory or a path specified by an environment variable
  `GMAIL_CREDENTIALS`.

---

## Non-Functional Requirements

- Single Python file, no custom package structure.
- Dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.
- No attachment downloading — filenames only.
- If fewer than 3 matching emails exist, return however many are found (no error).
- Graceful error message if authentication fails or the query returns no results.

---

## Out of Scope

- Downloading or saving attachment content.
- Pagination beyond the first page of results (the API default of up to 100
  results is sufficient for finding 3 matches).
- Support for multiple Gmail accounts.
- Interactive query input (query is always a CLI argument).
