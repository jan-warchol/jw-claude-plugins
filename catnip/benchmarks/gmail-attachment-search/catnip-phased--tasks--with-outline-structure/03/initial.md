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

**Must not:**
- Download or save attachment contents
- Modify, delete, or send any emails
- Require more than one credentials file from the user (a single `credentials.json` downloaded from Google Cloud Console)

## Solution

**Language & dependencies:**
- Python 3.8+
- `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`

**Auth flow:**
- Load `credentials.json` (OAuth 2.0 client secrets) from the working directory
- On first run, open browser for user consent; store resulting token in `token.json`
- On subsequent runs, load `token.json` and refresh if expired

**Search logic:**
1. Construct the effective query: `(<user_query>) has:attachment`
2. Call `users.messages.list` with `q=<effective_query>` and `maxResults=3`
3. For each message ID returned, call `users.messages.get` with `format=metadata` to fetch headers (Subject, From, Date)
4. Inspect `payload.parts` recursively to collect attachment filenames (parts where `filename` is non-empty)
5. Print results to stdout

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
- Downside: Gmail's IMAP has quirks; search syntax differs; attachment detection requires fetching full message body, which is slower and heavier than the Gmail API's metadata fetch

**`has:attachment` left to the user:**
- Simpler implementation — just pass the raw query through
- Rejected because the stated requirement is specifically to return emails *with* attachments, so enforcing this automatically is more correct

## Out of scope

- Downloading or saving attachment files
- Pagination (fetching more than 3 results)
- Support for multiple Gmail accounts
- Non-attachment metadata (labels, thread info, message body)
- Packaging as an installable CLI tool

## Uncertainty

- **What to do when fewer than 3 matching emails exist:** print however many are found, or surface an explicit "only N results found" message?
- **Token storage location:** hardcode `token.json` in the working directory, or make it configurable / use `~/.config/`?
- **Recursive attachment detection:** some emails nest parts deeply (inline images, multipart/mixed with multipart/alternative children). Should the script recurse into all parts, or only check top-level parts?
- **Attachment filter strictness:** should inline images (Content-Disposition: inline) be excluded, returning only proper file attachments?
