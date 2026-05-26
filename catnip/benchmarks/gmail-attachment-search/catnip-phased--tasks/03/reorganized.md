# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, searches for emails matching a user-supplied query string, filters those results to only emails that contain attachments, and prints metadata for the three most recent matches.

## Usage

**Input**: a query string as a positional CLI argument. Passed directly to the Gmail search API, so Gmail's full search syntax is supported (e.g. `from:boss@example.com`, `subject:invoice`, `has:attachment is:unread`).

```
python gmail_search.py "from:invoices@acme.com"
```

**Output**: printed to stdout for each of the (up to) 3 matched emails — Subject, Sender (`From` header), Date (`YYYY-MM-DD HH:MM`), and attachment filenames (comma-separated). Results are separated by a blank line.

```
Subject: Q2 Invoice
From: billing@acme.com
Date: 2026-03-14 09:22
Attachments: invoice_q2.pdf, terms.docx
```

If fewer than 3 matches exist, print however many there are. If none, print a clear message.

## Setup

**Dependencies**: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**Authentication**: uses OAuth 2.0 with scope `https://www.googleapis.com/auth/gmail.readonly`. Place `credentials.json` (downloaded from Google Cloud Console) in the working directory. On first run, a browser opens for the consent flow; the token is cached in `token.json` and refreshed automatically on subsequent runs.

**Assumption**: the user has a Google Cloud project with the Gmail API enabled and has downloaded `credentials.json`. If the project's OAuth consent screen is not published, only explicitly added test users can authenticate.

## Behaviour

1. Load/refresh OAuth token.
2. Call `users.messages.list` with the user's query, appending `has:attachment` if not already present (reduces unnecessary payload fetches). The API returns message IDs newest-first, up to 500 per page.
3. Iterate the results. For each message ID, fetch its full payload (`format=full`) and inspect `parts` for non-empty `filename` fields — these are treated as attachments.
4. Collect up to 3 such messages, then stop fetching.
5. Print formatted output for each.

If the first page of results (up to 500 messages) yields fewer than 3 with attachments, print however many were found. Fetching additional pages is out of scope.

## Error Handling

- Missing `credentials.json`: print an actionable error explaining how to obtain it from Google Cloud Console.
- No messages match the query: print "No emails found matching query."
- No matching messages have attachments: print "No matching emails with attachments found."
- Network or API errors: print the error message and exit with status code 1.

## Design Choices

**Gmail API over IMAP**: the Gmail API reuses Gmail's own query engine (labels, operators, full-text). IMAP `SEARCH` does not support Gmail-specific operators and requires managing a separate connection.

**Append `has:attachment` to query**: avoids fetching full payloads for non-attachment emails. The payload is still verified because the API's `has:attachment` match may include inline images that aren't true file attachments.

**Inline images heuristic**: the script counts any MIME part with a non-empty `filename` field as an attachment, regardless of `Content-Disposition`. This is a pragmatic heuristic that may occasionally include inline images.

**OAuth 2.0 over a service account**: service accounts require domain-wide delegation (Workspace admin access). OAuth 2.0 works for any personal or Workspace Gmail account.

## Out of Scope

- Downloading attachment content.
- Modifying or deleting emails.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts simultaneously.
- Interactive query input.
- Configurable result limit (hardcoded to 3 per the original requirement; `--limit N` deferred).
