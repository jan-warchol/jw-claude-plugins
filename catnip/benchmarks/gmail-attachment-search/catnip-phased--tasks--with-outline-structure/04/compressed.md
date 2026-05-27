# Gmail Attachment Search — Spec

## Objective

Python CLI script: takes a Gmail search query, returns the 3 most recent matching emails with attachments, printing sender, subject, date, and attachment filenames to stdout. Goal: quick command-line alternative to the Gmail web UI for locating attachments.

---

## Requirements

### Must do
- Accept a search query as a CLI argument or interactive prompt.
- Authenticate to Gmail via OAuth 2.0.
- Search all mail with the query.
- Return the 3 most recent emails with at least one attachment (messages, not threads).
- Print sender, subject, date, and attachment filenames for each match.
- If fewer than 3 found, print what exists with a trailing `Found N of 3 requested results.`
- If none found, print a message and exit 0.
- On auth failure or API error, print to stderr and exit non-zero.

### Must not do
- Modify, delete, or send emails.
- Store credentials in plain text.

---

## Solution

### Setup
Requires a Google Cloud project with the Gmail API enabled and OAuth 2.0 desktop credentials downloaded as `credentials.json`. If `credentials.json` is missing, print a pointer to the setup guide and exit.

Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

### Authentication
First run opens a browser OAuth consent flow; token saved to `token.json` for reuse. Credentials read from `credentials.json` in the working directory (`--credentials` flag overrides). Tokens refresh automatically; if revoked, the script deletes `token.json` and re-triggers the consent flow.

### Search & filtering
1. Prepend `has:attachment` to the query on `users.messages.list` — API-side filtering avoids wasteful `messages.get` calls.
2. Set `maxResults=20`; stop after the first page regardless of hits found.
3. Call `users.messages.get` with `format=metadata`; recursively traverse MIME parts and collect any with a non-empty `filename`. Named inline images are included — distinguishing them from true attachments requires fragile heuristics.
4. Each message is a separate result; multiple messages in the same thread each count independently.

### Output
Plain-text to stdout, one block per result:

```
[1] From: sender@example.com
    Subject: Invoice Q1
    Date: Mon, 12 May 2026 09:14:00 +0000
    Attachments: invoice_q1.pdf

Found 2 of 3 requested results.   ← only when < 3 found
```

---

## Alternative solutions considered

- **IMAP (`imaplib`)** — no extra dependencies, but requires manual IMAP enablement in Gmail settings, is being phased out, and OAuth setup is more complex.
- **`simplegmail` / wrappers** — less boilerplate, but extra dependency with less official support and less pagination control.

---

## Out of scope

- Multiple Gmail accounts.
- Pagination beyond `maxResults=20`.
- TUI or GUI.
- Packaging as a library or pip package.
- Test suite.

---

## Uncertainty

- **`maxResults` ceiling**: even with `has:attachment`, the first 20 API results may not contain 3 attachments if many are inline-image-only. Document as a known limitation.
