# Gmail Attachment Search Script

## Goal

A Python CLI script that accepts a search query and returns the 3 most recent Gmail
messages with attachments, showing date, sender, subject, and attachment filenames for
each.

## Requirements

1. Accepts query via CLI argument (`argparse`); prompts interactively if omitted.
2. Returns up to 3 most recent matching emails with attachments, newest-first; fewer
   if less exist.
3. Output per email: date received, sender, subject, attachment filenames.
4. No results: informative message, exit 0.
5. Missing `credentials.json`: message with setup instructions, exit 1.
6. API or network error: catch `HttpError`, print message, exit 1.
7. First run: browser OAuth consent flow; cache token in `token.json`, reuse and
   auto-refresh on subsequent runs.

## Solution

Use the Gmail API via `google-api-python-client` with OAuth 2.0 (`google-auth-oauthlib`).
Append `has:attachment` to the query before the API call so filtering is server-side.
Use `maxResults=3` as a server-side cap — not client-side truncation.

| Decision | Choice | Rationale |
|---|---|---|
| Scope | `gmail.readonly` | Minimum privilege — script is read-only |
| Filter | `has:attachment` server-side | Avoids fetching and discarding non-matching results |
| Cap | `maxResults=3` | Server-side limit; no pagination needed |
| Token | `token.json` | Avoids re-authorization on every run |

**Alternatives rejected:** Service account auth (cannot access personal Gmail inbox).
Client-side attachment filtering (inefficient vs. the `has:attachment` Gmail search
operator).

## Setup

1. In Google Cloud Console, enable the **Gmail API**.
2. Create **OAuth 2.0 credentials** (Desktop App type) and download `credentials.json`
   to the working directory.
3. Add `credentials.json` and `token.json` to `.gitignore`.

## Out of Scope

- Downloading attachment content
- Pagination
- Multiple Gmail accounts
- Modifying or sending emails

## Risks, Assumptions, and Open Questions

**Assumptions:** User has Google Cloud Console access. Gmail returns results
newest-first by default. Three results fit in the first API page with `maxResults=3`.

**Risks:** Token refresh failure if revoked (must re-run OAuth flow). Gmail indexing
lag may temporarily hide recently received emails from results.

**Open questions:** Should MIME types appear alongside filenames? Should result count
be configurable rather than fixed at 3?
