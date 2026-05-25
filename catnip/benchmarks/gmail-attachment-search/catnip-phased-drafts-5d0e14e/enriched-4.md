# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail, searches for emails
matching a user-provided query, and returns the most recent 3 matching emails
that contain attachments.

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
- Retrieve the most recent 3 messages matching the combined query, ordered
  by date descending (Gmail API default ordering).

### Output
For each of the (up to) 3 emails, print to stdout:
- Date sent (formatted as `YYYY-MM-DD`)
- Sender (`From:` header)
- Subject
- A list of attachment filenames

Separate consecutive results with a blank line. If no matching emails are
found, print `No emails found matching the query.` and exit with status 0.
On authentication or API errors, print a descriptive message to stderr and
exit with a non-zero status.

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

## Design Choices and Trade-offs

- **Single file**: Chosen for simplicity of deployment — no packaging or install
  step required beyond `pip install`.
- **Fixed count of 3**: Serves "quick recent-activity lookup" use cases without
  cluttering output. Making it configurable via a `--count` flag is deferred to
  keep the interface minimal.
- **OAuth 2.0 over service accounts**: Service accounts require domain-wide
  delegation and a server context; OAuth is the standard approach for personal-use
  CLI tools acting on behalf of a single user.
- **`gmail.readonly` scope**: Minimum required; limits exposure if `token.json`
  is compromised.
- **No pagination**: The API's default page size (up to 100 results) is sufficient
  to find 3 matches in virtually all real-world cases; implementing pagination
  would add complexity for negligible benefit.

---

## Assumptions and Risks

- **Assumption**: The user has a Google Cloud project with the Gmail API enabled
  and has already downloaded `credentials.json`.
- **Assumption**: Python 3.x and `pip` are available in the environment.
- **Risk**: `token.json` stores OAuth refresh tokens in plaintext; the script
  does not enforce file permissions beyond OS defaults.
- **Risk**: Transient Gmail API errors (quota, network) will surface as unhandled
  exceptions unless the error path prints a clear message and exits cleanly.

---

## Out of Scope

- Downloading or saving attachment content.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts.
- Interactive query input (query is always a CLI argument).
- Extracting or displaying email body text.
