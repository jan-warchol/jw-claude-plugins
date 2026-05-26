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
- Request the `https://www.googleapis.com/auth/gmail.readonly` scope — the minimum required; no write access is needed.
- On first run, open a browser window to complete the OAuth consent flow.
- Store the resulting token in a local file (`token.json`) so subsequent runs skip re-authentication. The file should have restrictive permissions (mode `0600`); the script should warn if it is world-readable.
- Require a `credentials.json` file (downloaded from Google Cloud Console) to be present in the working directory.

## Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Search query | CLI argument (`--query` / `-q`) or prompted interactively if omitted | Appended with `has:attachment` before sending to the API |
| `credentials.json` | File in working directory | OAuth client credentials from Google Cloud Console |

## Core logic

1. Build / refresh Gmail API credentials using `token.json` and `credentials.json`.
2. Append `has:attachment` to the user's query before passing it to the API. This reduces the candidate set server-side and avoids fetching metadata for irrelevant messages. The original query is shown to the user as-is; the modifier is invisible.
3. Call `users.messages.list` with the combined query and `maxResults=10`. Because `has:attachment` is injected, the first 10 API results should already be attachment-bearing messages; no large over-fetch is needed. If fewer than 3 results are returned, do not paginate further — report what was found.
4. For each returned message ID, call `users.messages.get` with `format=metadata`, requesting headers (`Subject`, `From`, `Date`) and MIME part metadata.
5. Determine whether the message has a real attachment by checking `payload.parts` (recursively for nested multipart bodies) for any part where `filename` is non-empty **and** `Content-Disposition` is `attachment`. Parts with `Content-Disposition: inline` (e.g. embedded images) are excluded from the attachment count but listed separately if present.
6. Collect messages that pass the filter; stop once 3 are accumulated or the candidate list is exhausted.
7. Display results (see Output section).

## Output

For each of the (up to) three matching emails, print a block like:

```
─────────────────────────────────────────
Subject     : Re: Q2 budget review
From        : alice@example.com
Date        : Mon, 19 May 2026 14:32:07 +0200
Attachments : budget_v3.xlsx, notes.pdf
─────────────────────────────────────────
```

If fewer than 3 matching emails exist, print all that are found plus a note: `(Only N matching email(s) found.)`.

If no matching emails are found, print: `No emails matching "<query>" with attachments were found.`

## Error handling

- Missing `credentials.json`: print a clear message explaining the file is required and how to obtain it, then exit with code 1.
- OAuth flow failure or token refresh failure: print the error and exit with code 1.
- Gmail API quota or network error: surface the error message and exit with code 1.
- Query returns zero messages before filtering: treat as "no results" case above.

## Design choices & trade-offs

**Injecting `has:attachment` vs. post-filtering:** Injecting the modifier into the API query is more efficient (fewer API calls, smaller result sets) and relies on Gmail's own attachment index. The trade-off is that Gmail's definition of "has attachment" may differ subtly from the script's own MIME inspection. If a message passes `has:attachment` but the MIME walk finds no `Content-Disposition: attachment` parts, it is silently skipped — this edge case is unlikely but possible with non-standard MIME structures.

**`format=metadata` vs. `format=full`:** Metadata format returns only headers and part descriptors, not body content. This keeps responses small and avoids unnecessary data transfer. Body content is never needed for this script's output.

**No pagination:** Limiting to `maxResults=10` and not following `nextPageToken` keeps the script simple. The assumption is that the first 10 `has:attachment` matches ordered by date are sufficient. A power user with very specific needs can refine their query to narrow results.

## Assumptions & open questions

**Assumptions:**
- The user has a Google Cloud project with the Gmail API enabled and has downloaded `credentials.json` as an "installed application" OAuth client.
- The script runs in an environment with a browser available for the initial OAuth flow (not a headless server).
- Gmail returns results ordered newest-first by default, which satisfies the "last 3" requirement without explicit date sorting.

**Open questions:**
- Should the script support a `--max` flag to return more than 3 results? Out of scope for now; hardcoded to 3.
- Should inline/embedded images count as attachments? Current decision: no — only `Content-Disposition: attachment` parts count.

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
