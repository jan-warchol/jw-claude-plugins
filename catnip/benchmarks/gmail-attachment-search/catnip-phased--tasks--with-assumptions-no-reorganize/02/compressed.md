# Gmail Attachment Search — Spec

## Objective

CLI Python script: accepts a Gmail search query, returns metadata for the 3 most recent matching emails with attachments. For quick scriptable access without the web UI.

## Requirements

**Must do:**
- Accept query via positional CLI arg or interactive prompt.
- Authenticate via OAuth 2.0 (Gmail API).
- Return up to 3 most recent matching emails with attachments; display subject, sender, date, attachment filename(s).
- Exit 0 with a message when fewer than 3 results exist; exit 1 with a message on error (missing credentials, auth failure, network).

**Must not:** download attachments; cache email content beyond the OAuth token; require server infrastructure.

## Solution

### Authentication
`google-auth` + `google-api-python-client`, OAuth 2.0. User provides `credentials.json` from Google Cloud Console (one-time setup); `token.json` is saved after the first browser-based consent flow. The library refreshes tokens automatically; an invalid refresh token re-triggers the browser flow. Missing `credentials.json` → setup hint + exit 1.

**Assumption:** user can complete the Cloud Console setup (create project, enable Gmail API, download credentials). API key access is not available for Gmail user data.

### Search and filtering
1. Append `has:attachment` to the query (documented in `--help`) and call `users.messages.list` with `maxResults=3`.
2. For each result call `users.messages.get` with `format=full`; collect filenames from `payload.parts`.

**Attachment definition:** parts with `filename` set and `Content-Disposition: attachment`. Inline images (`Content-Disposition: inline`) are excluded.

**Why `format=full`:** `format=metadata` does not reliably expose attachment part metadata; the extra transfer cost is acceptable for 3 messages.

### Output
```
[1] Subject: Re: Project files
    From: alice@example.com
    Date: 2026-05-25 14:32
    Attachments: report.pdf, budget.xlsx
```
No results → `No emails matching "<query>" with attachments found.`

### CLI & dependencies
```
python gmail_search.py "your search query"
```
Exit codes: 0 = success (incl. zero results), 1 = error. Python 3.8+.

Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Alternatives considered

- **IMAP:** no Cloud Console setup, but requires App Passwords (Workspace/legacy only) and weaker search. Rejected.
- **`simplegmail` / wrappers:** same OAuth flow, no benefit over the official client.

## Out of scope

Downloading attachments; pagination; multiple accounts; GUI; rate-limit/retry logic.

## Uncertainty

- **Delegated mailboxes:** only the authenticated user's own mailbox (`me`) is targeted.
- **Inline image edge cases:** senders may mark inline images as `attachment` disposition; the filename filter will include them with no further MIME-type classification.
