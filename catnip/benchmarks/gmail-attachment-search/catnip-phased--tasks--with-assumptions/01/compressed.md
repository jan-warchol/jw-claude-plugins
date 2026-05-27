# Gmail Attachment Search Script — Spec

## Objective

CLI Python script that queries Gmail and returns the 3 most recent emails with attachments matching a user-provided search string.

## Requirements

### Behavior
- Query via CLI argument; prompt interactively if omitted
- OAuth 2.0 (`gmail.readonly`); cache token in `token.json` (CWD); no re-auth on subsequent runs
- Auto-append `has:attachment` to query if absent; print a note when done
- Return up to 3 most-recent matches; report actual count if fewer found
- Per result: subject, sender, date, attachment filename(s)

### Constraints
- Read-only: no writes, no write scopes, no body/attachment data stored to disk
- No multi-account, GUI, or operations beyond search + display

### Error handling
- Missing `credentials.json`: actionable error with link to Google Cloud Console setup
- API errors (quota, network, invalid credentials): non-zero exit with message
- Result exhaustion below 3: report found count, don't fail silently

## Solution

### Authentication

Gmail API via `google-api-python-client` + `google-auth-oauthlib`. First run opens browser OAuth flow; token saved to `token.json` and reused. Scope: `https://www.googleapis.com/auth/gmail.readonly`.

**Assumption:** user has a Google Cloud project and `credentials.json` (standard requirement for personal Gmail API access).

### Search & filtering

1. Append `has:attachment` to query if absent; print `(added has:attachment to query)`.
2. `messages.list(userId="me", q=<query>, maxResults=10)` — results are most-recent-first by default.
3. For each ID, `messages.get(format="full")` → extract non-empty `filename` fields from MIME parts.
4. Collect 3 results; paginate via `nextPageToken` as needed.

### Output

```
(added has:attachment to query)

[1] Subject: Invoice March 2026
    From:    billing@example.com
    Date:    Wed, 12 Mar 2026 10:34:00 +0000
    Files:   invoice-march.pdf

[2] Subject: Project assets
    From:    designer@example.com
    Date:    Mon, 10 Mar 2026 08:12:00 +0000
    Files:   logo.png, banner.svg
```

### Dependencies
- `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

### Alternatives considered
- **IMAP (`imaplib`)**: OAuth over IMAP is harder to set up and lacks Gmail query syntax.
- **`simplegmail`**: simpler API but opaque, less maintained.

### Open questions
- **Extra API calls**: `has:attachment` matches inline images too; a message may pass the filter but yield no filenames, requiring more than 3 `messages.get` calls with no hard upper bound.
- **Inline images**: filter to `Content-Disposition: attachment` only, or accept all named MIME parts? (All named parts is simpler; confirm intent.)
