# Gmail Attachment Search — Spec

## Objective

A command-line Python script that accepts a Gmail search query from the user and returns metadata for the three most recent matching emails that contain at least one attachment.

Motivation: quick CLI access to Gmail attachments without navigating the web UI, suitable for scripting or ad-hoc lookups.

## Requirements

**Must do:**
- Accept a search query string from the user (CLI argument or stdin prompt).
- Authenticate with Gmail via OAuth 2.0 using the Gmail API.
- Search the user's mailbox using the provided query, restricted to emails with attachments.
- Return the 3 most recent such emails (or all available if fewer than 3 exist).
- For each result, display: subject, sender, date, and attachment filename(s).
- Print a clear message and exit cleanly (exit code 0) when fewer than 3 results are found.
- Print a clear message and exit with a non-zero code on errors (missing credentials, auth failure, network error).

**Must not:**
- Download attachment content.
- Store or cache email content locally beyond the OAuth token.
- Require server-side infrastructure; must run fully locally.

## Solution

### Authentication
Use `google-auth` + `google-api-python-client` with OAuth 2.0. The user provides a `credentials.json` file obtained from the Google Cloud Console (one-time setup). On first run the script opens a browser for the OAuth consent flow and saves a `token.json` for subsequent runs. The library handles token refresh automatically; if the refresh token is invalid the script re-triggers the browser flow.

If `credentials.json` is absent the script prints a setup hint and exits with code 1.

**Assumption:** the user is comfortable with the one-time Google Cloud Console setup (creating a project, enabling the Gmail API, downloading `credentials.json`). This is the only supported auth method — Gmail does not offer API key access for user data.

### Search and filtering
1. Append `has:attachment` to the user's query before calling `users.messages.list`. This is documented in `--help`.
2. Request the top 3 results (`maxResults=3`) — since the query already filters for attachments no over-fetching is needed.
3. For each result, call `users.messages.get` with `format=full` to inspect the `payload.parts` tree and collect attachment filenames.

**What counts as an attachment:** only parts with a `filename` field set and `Content-Disposition: attachment` (or equivalent). Inline images (`Content-Disposition: inline`) are excluded — they are presentational, not file attachments the user typically cares about.

**Why `format=full` over `format=metadata`:** `format=metadata` does not expose attachment part metadata reliably. The extra data transfer is acceptable for 3 messages.

### Output
Plain-text to stdout, one block per email:

```
[1] Subject: Re: Project files
    From: alice@example.com
    Date: 2026-05-25 14:32
    Attachments: report.pdf, budget.xlsx

[2] ...
```

If no results are found:
```
No emails matching "<query>" with attachments found.
```

### CLI interface
```
python gmail_search.py "your search query"
```
Positional argument; if omitted the script prompts interactively. Exit codes: `0` on success (including zero results), `1` on error.

**Assumption:** Python 3.8+.

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Alternative solutions considered

- **IMAP access:** avoids the Cloud Console setup but requires App Passwords (Workspace/legacy accounts only) and offers weaker search than Gmail's native query syntax. Rejected.
- **`simplegmail` / third-party wrappers:** still rely on the same OAuth flow underneath with no clear benefit over the official client.

## Out of scope

- Downloading or saving attachment files.
- Pagination (first page returns up to 100+ results; 3 will always be present unless the mailbox has fewer).
- Multiple Gmail accounts simultaneously.
- GUI or web interface.
- Rate-limit handling / retry logic.

## Uncertainty

- **Shared/delegated mailboxes:** the script targets the authenticated user's own mailbox (`me`). Delegated access is not considered.
- **Inline image classification edge cases:** some senders mark inline images as `attachment` disposition. The filename-based filter will include these; no attempt is made to further classify by MIME type.
