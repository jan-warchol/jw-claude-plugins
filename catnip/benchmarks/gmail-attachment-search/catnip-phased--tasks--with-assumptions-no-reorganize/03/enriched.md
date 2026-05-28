# Gmail Attachment Search Script

## Objective

A command-line Python script that accepts a Gmail search query from the user, searches the authenticated user's Gmail account, and prints a summary of the 3 most recent matching emails that contain at least one attachment. Intended as a quick utility for finding recent messages with files, without needing to navigate the Gmail UI.

## Requirements

**Must do:**
- Accept a search query string as input (CLI argument or interactive prompt)
- Search the authenticated user's Gmail using that query
- Filter results to only emails that have at least one attachment
- Print details of up to 3 most recent such emails (fewer if fewer exist)
- Display per email: subject, sender, date, and list of attachment filenames
- Authenticate with Gmail using OAuth2
- If no matching emails with attachments are found, print a clear "no results" message and exit cleanly

**Must not:**
- Download attachment contents (only report filenames/metadata)
- Modify or delete any emails
- Require storing credentials in plaintext

## Solution

Use the **Gmail API** (via `google-api-python-client`) with OAuth2 for authentication. The Gmail API's `messages.list` endpoint accepts Gmail search syntax directly, making it straightforward to pass the user's query through unchanged.

**Authentication:** OAuth2 via `google-auth-oauthlib`. Credentials stored in a local `token.json` after first-time browser-based consent flow. `credentials.json` (downloaded from Google Cloud Console) must be present. The `google-auth` library handles token refresh automatically when the access token expires; no special handling needed.

**Flow:**
1. Load or obtain OAuth2 credentials (scopes: `gmail.readonly`)
2. Accept query string from `sys.argv[1]` (or prompt if not provided)
3. Call `users.messages.list` with the combined query; paginate until 3 attachment-bearing emails found or results exhausted
4. For each candidate message, fetch the full payload (`format=full`) and inspect `parts` for MIME parts where `filename` is non-empty
5. Collect up to 3 matches; print formatted summary

**Key detail — filtering for attachments:** The Gmail search query `has:attachment` is automatically appended to the user's query to pre-filter at the API level, reducing unnecessary fetches.

**Error handling:**
- Missing `credentials.json`: print a descriptive message explaining the setup step required and exit with a non-zero code
- API errors (network failure, quota exceeded): print the error message and exit; no retry logic
- Authentication failure or cancelled consent: print error and exit

**Output format (printed to stdout):**
```
[1] Subject: Re: Q3 Report
    From: alice@example.com
    Date: 2026-05-20
    Attachments: q3_report.pdf, notes.docx

[2] ...
```

**Dependencies:**
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Alternative solutions considered

- **IMAP (imaplib):** Standard library, no API quota, but Gmail's IMAP support requires enabling "less secure app access" or an app password, making OAuth2 setup comparable in complexity. Gmail API offers richer metadata and native search syntax support, so preferred.
- **Gmail API with `has:attachment` as a post-filter only:** Fetching all matching messages and filtering in Python is wasteful. Appending `has:attachment` to the query is cleaner and reduces API calls.

## Out of scope

- Downloading or saving attachment files
- Sending or replying to emails
- Handling multiple Gmail accounts simultaneously
- A GUI or web interface
- Retry logic or offline resilience

## Uncertainty

- **`credentials.json` setup:** The user must create a Google Cloud project, enable the Gmail API, and download OAuth credentials. Assumption: the user is comfortable with this one-time setup, or the script's error message will guide them.
- **Search scope — inbox vs. all mail:** The requirements mention "inbox," but `users.messages.list` searches all mail (including Sent, Spam, etc.) unless restricted with an `in:inbox` clause. Appending `has:attachment` without `in:inbox` will match emails in all folders. Assumption: searching all mail is the more useful default; the user can add `in:inbox` to their query if needed.
- **"Last 3":** Interpreted as the 3 most recent by receive date among results matching the combined query. Gmail API returns results newest-first by default.
- **Attachment definition:** Any MIME part with a non-empty `filename` field. Inline images with filenames count; embedded message bodies do not. This matches typical user expectation of "attachment."
- **Query input method:** CLI argument (`sys.argv[1]`) with fallback to `input()` prompt. No complex argparse needed given the "simple script" framing.
- **API quota:** Gmail API has a daily quota (1 billion quota units/day for personal use). Fetching a message with `format=full` costs ~5 units. For 3 results this is negligible, but worth noting for users running the script repeatedly in automation.
