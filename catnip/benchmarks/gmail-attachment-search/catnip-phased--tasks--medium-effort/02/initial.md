# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via the Google API, searches for emails matching a user-supplied query string, filters results to only those containing attachments, and prints details of the three most recent matching emails.

## Goals

- Accept a search query from the user (command-line argument or interactive prompt).
- Use the Gmail API to search the authenticated user's mailbox.
- Filter results to emails that have at least one attachment.
- Return the three most recent such emails, ordered newest-first.
- Display useful information about each match: subject, sender, date, and attachment filename(s).

## Non-goals

- Downloading or saving attachment content to disk.
- Sending, modifying, or deleting emails.
- Supporting multiple Gmail accounts simultaneously.
- Building a reusable library or importable module; this is a standalone script.

## Authentication

- Use OAuth 2.0 via `google-auth-oauthlib` and the Gmail API.
- On first run, open a browser window to complete the OAuth consent flow.
- Store the resulting token in a local file (`token.json`) so subsequent runs skip re-authentication.
- Require a `credentials.json` file (downloaded from Google Cloud Console) to be present in the working directory.

## Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Search query | CLI argument (`--query` / `-q`) or prompted interactively if omitted | Passed verbatim to the Gmail API `q` parameter |
| `credentials.json` | File in working directory | OAuth client credentials from Google Cloud Console |

## Core logic

1. Build / refresh Gmail API credentials using `token.json` and `credentials.json`.
2. Call `users.messages.list` with the user's query and `maxResults` large enough to find at least 3 matches (default: fetch up to 100 candidates, then filter).
3. For each returned message ID, call `users.messages.get` with `format=metadata` to retrieve headers and part metadata.
4. Determine whether the message has an attachment by checking `payload.parts` for any part whose `filename` is non-empty.
5. Collect messages that pass the filter; stop once 3 are accumulated or the candidate list is exhausted.
6. Display results (see Output section).

## Output

For each of the (up to) three matching emails, print a block like:

```
─────────────────────────────────────────
Subject   : Re: Q2 budget review
From      : alice@example.com
Date      : Mon, 19 May 2026 14:32:07 +0200
Attachments: budget_v3.xlsx, notes.pdf
─────────────────────────────────────────
```

If fewer than 3 matching emails exist, print all that are found plus a note: `(Only N matching email(s) found.)`.

If no matching emails are found, print: `No emails matching "<query>" with attachments were found.`

## Error handling

- Missing `credentials.json`: print a clear message explaining the file is required and how to obtain it, then exit with code 1.
- OAuth flow failure or token refresh failure: print the error and exit with code 1.
- Gmail API quota or network error: surface the error message and exit with code 1.
- Query returns zero messages before filtering: treat as "no results" case above.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

All installable via `pip install`.

## File layout

```
gmail_search.py        # main script
credentials.json       # user-provided, not committed
token.json             # auto-generated on first run, not committed
```

## Usage example

```bash
# With argument
python gmail_search.py --query "invoice 2026"

# Interactive prompt
python gmail_search.py
Enter search query: invoice 2026
```
