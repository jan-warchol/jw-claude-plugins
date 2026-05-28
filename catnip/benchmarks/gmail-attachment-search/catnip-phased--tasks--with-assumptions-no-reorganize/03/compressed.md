# Gmail Attachment Search Script

## Objective

CLI Python script that accepts a Gmail search query and prints a summary of the 3 most recent matching emails with attachments. Quick alternative to navigating the Gmail UI.

## Requirements

**Must do:**
- Accept a query via CLI arg or interactive prompt
- Search the authenticated user's Gmail and filter to emails with at least one attachment
- Print up to 3 results (fewer if fewer exist); show subject, sender, date, attachment filenames per email
- Print a clear "no results" message if none found
- Authenticate via OAuth2

**Must not:**
- Download attachment contents
- Modify or delete emails
- Store credentials in plaintext

## Solution

**Gmail API** (`google-api-python-client`) with OAuth2 (`google-auth-oauthlib`). `messages.list` accepts Gmail search syntax natively.

**Auth:** First run opens a browser consent flow; credentials cached in `token.json`. `credentials.json` (from Google Cloud Console) must be present. `google-auth` handles token refresh automatically.

**Flow:**
1. Load/obtain OAuth2 credentials (scope: `gmail.readonly`)
2. Read query from `sys.argv[1]` or `input()`
3. Append `has:attachment` to the query; call `users.messages.list`; paginate until 3 matches found or results exhausted
4. Fetch each candidate with `format=full`; collect MIME parts with non-empty `filename`
5. Print formatted summary of up to 3 results

**Output:**
```
[1] Subject: Re: Q3 Report
    From: alice@example.com
    Date: 2026-05-20
    Attachments: q3_report.pdf, notes.docx
```

**Error handling:** On missing `credentials.json`, auth failure, or API error — print a descriptive message and exit non-zero. No retries.

**Dependencies:** `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

## Alternative solutions considered

- **IMAP (`imaplib`):** No API quota, but requires app passwords or "less secure app" access. Gmail API's native search support and richer metadata make it the better fit.
- **Post-filter only (no `has:attachment` in query):** Wasteful; appending it pre-filters at the API level.

## Out of scope

Downloading attachments, sending/replying, multiple accounts, GUI, retry logic.

## Uncertainty

- **Setup:** Requires a Google Cloud project with Gmail API enabled and `credentials.json` downloaded. Assumed the user can handle this one-time step.
- **Search scope:** `messages.list` searches all mail, not just inbox. Assumption: all-mail is more useful; users can add `in:inbox` to their query if needed.
- **"Last 3":** Most recent 3 by receive date. Gmail API returns newest-first by default.
- **Attachment definition:** Any MIME part with a non-empty `filename`. Inline images count; embedded bodies do not.
- **API quota:** `format=full` costs ~5 quota units/message. Negligible for 3 results; only relevant if scripted at high frequency.
