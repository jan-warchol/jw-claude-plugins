# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, searches for emails matching a user-supplied query string, filters those results to only emails that contain attachments, and prints metadata for the three most recent matches.

## Inputs

- **Query string**: provided as a command-line argument (positional). Passed directly to Gmail's search API, so Gmail's full search syntax is supported (e.g. `from:boss@example.com`, `subject:invoice`, `has:attachment is:unread`).
- The script automatically appends `has:attachment` to the query if not already present, reducing unnecessary API calls. It still verifies attachment presence in the fetched payload to guard against inline images being treated as attachments by the API.

## Outputs

Printed to stdout for each of the (up to) 3 matched emails:

- Subject
- Sender (`From` header)
- Date (formatted as `YYYY-MM-DD HH:MM`)
- List of attachment filenames (comma-separated on one line)

Results are separated by a blank line. If fewer than 3 emails with attachments match, print however many exist. If none match, print a clear message.

**Example output:**
```
Subject: Q2 Invoice
From: billing@acme.com
Date: 2026-03-14 09:22
Attachments: invoice_q2.pdf, terms.docx
```

## Authentication

- Uses the Gmail API with OAuth 2.0.
- Credentials file: `credentials.json` in the working directory (downloaded from Google Cloud Console).
- Token cached in `token.json` in the working directory; refreshed automatically when expired.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- **Assumption**: the user has a Google Cloud project with the Gmail API enabled and has downloaded `credentials.json`. The first run opens a browser for the OAuth consent flow; subsequent runs use the cached token.

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- `google-api-python-client`

Install via: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`

## Behaviour

1. Load/refresh OAuth token.
2. Call `users.messages.list` with the user's query (with `has:attachment` appended if absent). The API returns message IDs in reverse-chronological order (newest first) — up to 500 per page.
3. Iterate the results. For each message ID, fetch its full payload (`format=full`) and inspect `parts` for `filename` fields that are non-empty — these are true attachments.
4. Collect up to 3 such messages, then stop fetching.
5. Print formatted output for each.

If the first page of results (up to 500 messages) contains fewer than 3 with attachments, print however many were found. Fetching additional pages is out of scope.

## Error Handling

- Missing `credentials.json`: print an actionable error message explaining how to obtain it from Google Cloud Console.
- No messages match the query: print "No emails found matching query."
- No messages with attachments among matches: print "No matching emails with attachments found."
- Network or API errors: print the error message and exit with status code 1.

## Design Choices

**Gmail API over IMAP**: The Gmail API provides a reliable search interface reusing Gmail's own query engine (labels, operators, full-text). IMAP search is weaker (IMAP `SEARCH` does not support Gmail-specific operators) and requires managing a separate IMAP connection.

**Append `has:attachment` to query**: Avoids fetching and parsing full message payloads for non-attachment emails. The payload still gets verified because Gmail may count certain inline images as attachments in search but not in the payload structure.

**OAuth 2.0 over a service account**: Service accounts require domain-wide delegation, which needs Workspace admin access. OAuth 2.0 works for any personal or Workspace Gmail account.

## Out of Scope

- Downloading attachment content.
- Modifying or deleting emails.
- Pagination beyond the first page of results (up to 500 messages).
- Support for multiple Gmail accounts simultaneously.
- Interactive query input (query must be provided as a CLI argument).

## Risks and Open Questions

- **OAuth consent screen in test mode**: if the Google Cloud project's consent screen is not published, only explicitly added test users can authenticate. Users should be aware of this limitation.
- **Inline images vs. attachments**: some emails embed images as MIME parts with filenames but `Content-Disposition: inline`. The script counts only parts with a non-empty `filename` field regardless of disposition — this is a pragmatic heuristic that may occasionally include inline images.
- **Open question**: should the script accept `--limit N` to make the result count configurable rather than hardcoding 3? Deferred; hardcoded for now per the original requirement.
