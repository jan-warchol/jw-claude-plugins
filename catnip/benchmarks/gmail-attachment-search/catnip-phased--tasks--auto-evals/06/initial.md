# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, runs a user-supplied search query, and prints the three most recent matching emails that contain at least one attachment.

## Authentication

- Uses the Gmail API via `google-auth` and `google-api-python-client`.
- OAuth 2.0 credentials are read from a `credentials.json` file (downloaded from Google Cloud Console).
- On first run, opens a browser for user consent; stores the resulting token in `token.json` for subsequent runs.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Inputs

| Input | Source | Notes |
|---|---|---|
| Search query | Command-line argument (`--query` / `-q`) | Passed directly to the Gmail API `q` parameter |

Example invocation:
```
python gmail_search.py --query "invoice from:billing@example.com"
```

## Core Logic

1. Authenticate and build the Gmail API service.
2. Call `users.messages.list` with the user query; request up to 100 results (newest first).
3. For each message (in order), fetch the full message via `users.messages.get` with `format=full`.
4. Check whether the message has any `PART` with `filename` set (non-empty) — this indicates an attachment.
5. Collect messages that pass the attachment check.
6. Stop once 3 such messages have been found, or all results are exhausted.

## Output

For each of the (up to 3) matching emails, print:

```
--- Email 1 ---
Date:    <date>
From:    <sender>
Subject: <subject>
Attachments:
  - filename.pdf (application/pdf, 45 KB)
  - photo.jpg (image/jpeg, 200 KB)
```

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to the Google Cloud Console setup guide, then exit.
- No matching emails found: print `"No emails found matching query: <query>"`.
- Fewer than 3 matching emails with attachments: print however many were found.
- API errors: surface the error message and exit with a non-zero code.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## File Structure

```
gmail_search.py       # main script
credentials.json      # OAuth client secret (user-provided, not committed)
token.json            # stored OAuth token (auto-generated, not committed)
requirements.txt      # pip dependencies
```
