# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, searches for emails matching a user-supplied query string, filters those results to only emails that contain attachments, and prints metadata for the three most recent matches.

## Inputs

- **Query string**: provided as a command-line argument (positional). Passed directly to Gmail's search API, so Gmail's full search syntax is supported (e.g. `from:boss@example.com`, `subject:invoice`, `has:attachment is:unread`).

## Outputs

Printed to stdout for each of the (up to) 3 matched emails:

- Subject
- Sender (`From` header)
- Date
- List of attachment filenames

If fewer than 3 emails with attachments match, print however many exist. If none match, print a clear message.

## Authentication

- Uses the Gmail API with OAuth 2.0.
- Credentials file: `credentials.json` in the working directory (downloaded from Google Cloud Console).
- Token cached in `token.json` in the working directory; refreshed automatically when expired.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- `google-api-python-client`

Install via: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`

## Behaviour

1. Load/refresh OAuth token.
2. Call `users.messages.list` with the user's query. The API may return emails without attachments; the script must check each one.
3. Iterate results in reverse-chronological order (Gmail API default). For each message, fetch its full payload and inspect `parts` for `filename` fields that are non-empty — these are attachments.
4. Collect up to 3 such messages.
5. Print formatted output for each.

## Error Handling

- Missing `credentials.json`: print an actionable error message explaining how to obtain it.
- No messages match the query: print "No emails found matching query."
- No messages with attachments among matches: print "No matching emails with attachments found."
- API errors: print the error and exit with a non-zero status code.

## Usage Example

```
python gmail_search.py "from:invoices@acme.com"
```

## Out of Scope

- Downloading attachment content.
- Modifying or deleting emails.
- Pagination beyond the first page of results (Gmail API returns up to 500 results per page; sufficient for most queries).
