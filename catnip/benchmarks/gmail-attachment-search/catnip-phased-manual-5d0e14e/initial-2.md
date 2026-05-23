# Gmail Attachment Search Script

## Overview

A command-line Python script that searches a user's Gmail inbox using a provided query string and returns the three most recent matching emails that contain attachments.

## Functional Requirements

- Accept a search query string as a command-line argument
- Authenticate with the Gmail API using OAuth 2.0
- Search Gmail for messages matching the query
- Filter results to only include messages that have at least one attachment
- Return the three most recent such messages
- Display for each result: sender, date, subject, and attachment filenames

## Interface

```
python search_attachments.py "<query>"
```

Example:
```
python search_attachments.py "from:boss@company.com invoice"
```

Output format (one block per email):
```
Date:        2024-03-15
From:        boss@company.com
Subject:     Q1 Invoice
Attachments: invoice_q1.pdf, receipt.png
```

If fewer than 3 matching emails with attachments are found, display however many exist. If none are found, print a clear "no results" message.

## Authentication

- Use the Gmail API with OAuth 2.0
- Store credentials in a local `token.json` file so the user only authenticates once
- Require a `credentials.json` file (downloaded from Google Cloud Console) to be present in the working directory
- Request read-only Gmail scope (`gmail.readonly`)

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- No other third-party libraries

## Out of Scope

- Downloading or saving attachments to disk
- Pagination beyond what is needed to find 3 results
- Support for multiple Gmail accounts
- Any GUI or interactive interface
