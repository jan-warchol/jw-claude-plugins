# Gmail Attachment Search — Spec

## Objective

A single-file Python CLI script that accepts a Gmail search query from the user, searches the authenticated account via the Gmail API, and prints summary information for the three most recent matching emails that contain attachments.

Motivation: quickly surface relevant emails with files attached without opening a browser, useful in automation pipelines or daily workflows.

## Requirements

**Must:**
- Accept a search query string as a CLI argument
- Authenticate with Gmail using OAuth 2.0 (standard Google API flow)
- Combine the user query with `has:attachment` so only emails with attachments are returned
- Return at most the 3 most recent matching emails
- For each match, display: subject, sender, date, and attachment filename(s)
- Persist the OAuth token locally so re-authentication is not required on every run
- Print a clear message when zero results are found
- Exit with a non-zero status code on unrecoverable errors (missing credentials file, API failure)

**Must not:**
- Download or save attachment contents
- Modify, delete, or send any emails
- Require more than one credentials file from the user (a single `credentials.json` downloaded from Google Cloud Console)

## Solution

**Prerequisites (user setup):**
- A Google Cloud project with the Gmail API enabled
- An OAuth 2.0 client ID (Desktop app type) downloaded as `credentials.json` and placed in the working directory
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

**Language & dependencies:**
- Python 3.8+
- `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`

**Auth flow:**
- Load `credentials.json` from the working directory; print a clear error and exit if not found
- On first run, open browser for user consent; store resulting token in `token.json` in the working directory
- On subsequent runs, load `token.json` and refresh if expired

**Search logic:**
1. Construct the effective query: `(<user_query>) has:attachment`
2. Call `users.messages.list` with `q=<effective_query>` and `maxResults=3`
3. For each message ID returned, call `users.messages.get` with `format=full` to fetch the complete payload (headers + parts)
4. Extract Subject, From, Date from headers
5. Recurse through `payload.parts` to collect attachment filenames — a part is a proper attachment when `filename` is non-empty and `Content-Disposition` is `attachment` (skip inline images)
6. Print results to stdout; if the API returns fewer than 3 results, print however many were found with a "(N of 3 results)" note

**Note on `format=full` vs `format=metadata`:** `metadata` only returns headers and does not populate `payload.parts`, so attachment filenames cannot be extracted from it. `format=full` is required despite being a slightly heavier fetch.

**Output format (plain text):**
```
[1] Subject: ...
    From: ...
    Date: ...
    Attachments: file1.pdf, file2.xlsx

[2] ...
```

**CLI interface:**
```
python gmail_search.py "invoice from:accounting"
```

## Alternative solutions considered

**IMAP instead of Gmail API:**
- Python's built-in `imaplib` + `email` modules, no external dependencies
- Downside: Gmail's IMAP has quirks; search syntax differs; attachment detection requires fetching full message bodies, which is slower; IMAP access must be explicitly enabled in Gmail settings

**`has:attachment` left to the user:**
- Simpler implementation — just pass the raw query through
- Rejected because the stated goal is specifically to return emails *with* attachments, so enforcing this automatically is more correct and avoids user error

## Out of scope

- Downloading or saving attachment files
- Pagination (fetching more than 3 results)
- Support for multiple Gmail accounts
- Non-attachment metadata (labels, thread info, message body)
- Packaging as an installable CLI tool
- Configurable result count

## Uncertainty

- **Token/credentials path:** hardcoded to the working directory for simplicity; a `~/.config/gmail-search/` location would be cleaner for repeated use across directories but adds complexity. Resolve by hardcoding working directory for now.
- **Recursive depth for attachment detection:** recurse into all nested `multipart/*` parts to handle complex MIME trees (multipart/mixed containing multipart/alternative, etc.).
- **API rate limits:** Gmail API has a default quota of 250 quota units/second per user; fetching 3 full messages costs ~15 units total, well within limits. Not a concern for this use case.
