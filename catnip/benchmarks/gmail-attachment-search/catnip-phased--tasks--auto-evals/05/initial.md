# Gmail Attachment Search — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, searches for emails matching a user-supplied query, and prints the last 3 matching emails that contain at least one attachment.

## Authentication

- Uses the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- On first run, opens a browser for OAuth2 consent and saves credentials to `token.json`.
- On subsequent runs, loads credentials from `token.json`, refreshing the access token automatically if expired.
- Requires a `credentials.json` file (downloaded from Google Cloud Console) in the working directory.

## Inputs

- **Query string**: passed as a command-line argument (required). Any valid Gmail search query is accepted (e.g. `from:alice subject:invoice`).

## Behavior

1. Authenticate with the Gmail API (read-only scope: `https://www.googleapis.com/auth/gmail.readonly`).
2. Search messages using the provided query, requesting up to 100 results sorted by most-recent first (default Gmail API ordering).
3. For each result (in order, newest first), fetch the full message payload and inspect MIME parts.
4. Collect the first 3 messages that have at least one attachment (a MIME part with a `filename` field).
5. Stop fetching further messages once 3 qualifying messages are found or the result list is exhausted.
6. Print the results (see Output section).

## Output

For each of the (up to) 3 qualifying emails, print:

```
Subject: <subject>
From:    <sender>
Date:    <date>
Attachments:
  - <filename1> (<mime-type>, <size> bytes)
  - <filename2> ...
---
```

If no matching emails with attachments are found, print:

```
No emails with attachments found matching: <query>
```

## Error Handling

- Missing `credentials.json`: print a clear error message explaining where to obtain the file and exit with code 1.
- Gmail API errors (network issues, quota exceeded): print the error and exit with code 1.
- Invalid or empty query: accepted as-is; Gmail will return zero results, triggering the "no results" message.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Usage Example

```bash
python gmail_search.py "from:alice has:attachment"
```
