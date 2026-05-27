# Gmail Attachment Search — Spec

## Objective

Single-file Python CLI that accepts a Gmail search query, searches via the Gmail API, and prints the 3 most recent matching emails with attachments. Useful for surfacing relevant files without opening a browser or in automation pipelines.

## Requirements

**Must:**
- Accept a search query as a CLI argument
- Authenticate via OAuth 2.0; persist token so subsequent runs skip re-auth
- Append `has:attachment` to the query automatically
- Return at most 3 most recent matches; note when fewer exist
- Display per match: subject, sender, date, attachment filename(s)
- Exit non-zero with a clear message on unrecoverable errors (missing credentials, API failure)

**Must not:**
- Download attachment contents or modify/send emails
- Require more than `credentials.json` from the user

## Solution

### Setup & dependencies

- Python 3.8+; `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`
- Google Cloud project with Gmail API enabled; OAuth 2.0 Desktop client downloaded as `credentials.json` in the working directory
- Scope: `https://www.googleapis.com/auth/gmail.readonly`

### Authentication

- Load `credentials.json` from the working directory; error and exit if missing
- First run: browser consent flow; save token to `token.json` (working directory)
- Subsequent runs: load and auto-refresh `token.json`

### Search & result extraction

1. Effective query: `(<user_query>) has:attachment`
2. `users.messages.list` with `q=<query>`, `maxResults=3`
3. `users.messages.get` with `format=full` for each result (headers + parts)
4. Extract Subject, From, Date from headers
5. Recurse all `payload.parts` (including nested `multipart/*`); collect filenames where `filename` is non-empty and `Content-Disposition` is `attachment` (skip inline images)

### Interface

```
python gmail_search.py "invoice from:accounting"
```
```
[1] Subject: ...
    From: ...
    Date: ...
    Attachments: file1.pdf, file2.xlsx
```

## Alternatives considered

**IMAP:** no extra dependencies, but Gmail IMAP has quirks, different search syntax, requires full body fetch for attachment detection, and must be explicitly enabled in Gmail settings.

**User supplies `has:attachment`:** simpler, but the script's purpose is specifically attachment search — enforcing it automatically avoids user error.

**`format=metadata`:** lighter call, but doesn't populate `payload.parts`; attachment filenames are inaccessible. `format=full` is required.

## Out of scope

Downloading attachments · pagination · multiple accounts · labels/thread/body metadata · installable packaging · configurable result count
