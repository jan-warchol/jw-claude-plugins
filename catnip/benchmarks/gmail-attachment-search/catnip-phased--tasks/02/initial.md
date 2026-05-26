# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail, searches for emails matching a user-supplied query, and prints the last 3 matching emails that contain attachments.

## Functional Requirements

### Input

- The user provides a search query as a command-line argument (e.g. `python search_gmail.py "from:boss subject:report"`).
- The query follows Gmail search syntax (same as the Gmail search box).

### Processing

1. Authenticate with the Gmail API using OAuth 2.0.
2. Execute the search query via the Gmail API (`messages.list` with the `q` parameter).
3. Filter results to only those messages that have at least one attachment.
4. Return the **3 most recent** matching messages (newest first).

### Output

For each of the up to 3 results, print to stdout:
- Message date
- Sender (`From` header)
- Subject
- List of attachment filenames and their MIME types

### Edge Cases

- Fewer than 3 matching messages with attachments: return however many exist.
- No matching messages with attachments: print a clear "no results" message.
- Network or API errors: print an error message and exit with a non-zero code.

## Authentication

- Uses the Gmail API with OAuth 2.0.
- Requires a `credentials.json` file (downloaded from Google Cloud Console) in the working directory.
- On first run, opens a browser for the user to authorize access; stores the token in `token.json` for subsequent runs.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- `google-api-python-client`

## Non-Goals

- Downloading attachment contents.
- Modifying or deleting emails.
- Sending emails.
- Supporting multiple Gmail accounts simultaneously.
