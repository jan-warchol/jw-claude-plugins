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

### Setup & dependencies

- Python 3.8+
- `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`
- A Google Cloud project with the Gmail API enabled; OAuth 2.0 client ID (Desktop app type) downloaded as `credentials.json` in the working directory
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

### Authentication

- Load `credentials.json` from the working directory; print a clear error and exit if not found
- On first run, open browser for user consent; store resulting token in `token.json` in the working directory
- On subsequent runs, load `token.json` and refresh if expired
- Token and credentials files are hardcoded to the working directory for simplicity

### Search & result extraction

1. Construct the effective query: `(<user_query>) has:attachment`
2. Call `users.messages.list` with `q=<effective_query>` and `maxResults=3`
3. For each message ID returned, call `users.messages.get` with `format=full` to fetch the complete payload (headers + parts)
4. Extract Subject, From, Date from message headers
5. Recurse through all nested `payload.parts` (including nested `multipart/*` subtrees) to collect attachment filenames — a part qualifies when `filename` is non-empty and `Content-Disposition` is `attachment` (inline images are skipped)
6. If the API returns fewer than 3 results, print however many were found with a "(N of 3 results)" note

### Interface

**CLI:**
```
python gmail_search.py "invoice from:accounting"
```

**Output (plain text, stdout):**
```
[1] Subject: ...
    From: ...
    Date: ...
    Attachments: file1.pdf, file2.xlsx

[2] ...
```

## Alternative solutions considered

**IMAP instead of Gmail API:**
- Python's built-in `imaplib` + `email` modules, no external dependencies
- Rejected: Gmail's IMAP has quirks; search syntax differs; attachment detection requires fetching full message bodies (slower); IMAP access must be explicitly enabled in Gmail settings

**`has:attachment` left to the user:**
- Simpler — just pass the raw query through
- Rejected: the stated goal is specifically to return emails with attachments, so enforcing this automatically is more correct and avoids user error

**`format=metadata` instead of `format=full` for message fetch:**
- `metadata` returns only headers and is a lighter API call
- Rejected: `metadata` does not populate `payload.parts`, so attachment filenames cannot be extracted from it; `format=full` is required

## Out of scope

- Downloading or saving attachment files
- Pagination (fetching more than 3 results)
- Support for multiple Gmail accounts
- Non-attachment metadata (labels, thread info, message body)
- Packaging as an installable CLI tool
- Configurable result count
