# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the three most recent emails matching that query which contain at least one attachment. Each result includes the sender, subject, date, and a list of attachment filenames.

## Functional Requirements

### Input
- A single positional CLI argument: the Gmail search query string (e.g., `"from:boss invoice"`).
- The query follows Gmail's standard search syntax, passed through unchanged to the API.

### Processing
1. Authenticate with the Gmail API using OAuth2 (credentials stored locally).
2. Call the Gmail API `users.messages.list` endpoint with the user-supplied query.
3. From the returned message list, fetch full message details (headers + parts) in order from newest to oldest.
4. Filter to messages that have at least one attachment (i.e., a `MIME` part with a `filename`).
5. Stop after collecting 3 such messages.

### Output
Print to stdout a structured summary for each of the up to 3 matched messages:

```
--- Email 1 ---
From:    alice@example.com
Subject: Q1 Invoice
Date:    Mon, 12 May 2025 09:14:03 +0000
Attachments:
  - invoice_q1.pdf (application/pdf)
  - terms.docx (application/vnd.openxmlformats...)
```

If fewer than 3 matching emails are found, print however many exist. If none are found, print a clear message: `No matching emails with attachments found.`

## Authentication

- Use `google-auth-oauthlib` and `google-api-python-client`.
- On first run, open a browser for OAuth2 consent and save the resulting token to `token.json` in the working directory.
- On subsequent runs, load `token.json` and refresh automatically if expired.
- Required OAuth2 scope: `https://www.googleapis.com/auth/gmail.readonly`.
- The script reads `credentials.json` (downloaded from Google Cloud Console) from the working directory.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Usage

```
python gmail_search.py "<query>"
```

Example:

```
python gmail_search.py "has:attachment from:finance"
```

## Error Handling

- Missing `credentials.json`: print an instructional error and exit with code 1.
- API errors (quota exceeded, network failure): print the error message and exit with code 1.
- Invalid or empty query string: print usage hint and exit with code 1.

## Non-Goals

- Downloading attachment content.
- Pagination beyond what is needed to find 3 results.
- Support for multiple Gmail accounts.
- Any GUI or interactive mode.
