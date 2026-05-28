# Gmail Attachment Search — Spec

## Objective

A command-line Python script that accepts a Gmail search query from the user and returns metadata (and optionally content) for the three most recent matching emails that contain at least one attachment.

Motivation: quick CLI access to Gmail attachments without navigating the web UI, suitable for scripting or ad-hoc lookups.

## Requirements

**Must do:**
- Accept a search query string from the user (CLI argument or stdin prompt).
- Authenticate with Gmail via OAuth 2.0 using the Gmail API (Google's official approach for programmatic access).
- Search the user's Gmail inbox using the provided query.
- Filter results to only emails that have at least one attachment.
- Return the 3 most recent such emails.
- For each result, display: subject, sender, date, and attachment filename(s).

**Must not:**
- Download attachment content (unless explicitly requested — out of scope for now).
- Store or cache email content locally beyond the OAuth token.
- Require server-side infrastructure; must run fully locally.

## Solution

### Authentication
Use the `google-auth` + `google-api-python-client` libraries with OAuth 2.0. The user provides a `credentials.json` file obtained from the Google Cloud Console (a one-time setup step). On first run, the script opens a browser for the OAuth consent flow and saves a `token.json` for subsequent runs.

**Assumption:** the user is comfortable with the one-time Google Cloud Console setup (creating a project, enabling the Gmail API, downloading `credentials.json`). This is the only supported auth method — Gmail does not offer API key access for user data.

### Search and filtering
1. Call `users.messages.list` with the user's query string. The Gmail API's `q` parameter accepts the same syntax as the Gmail search box.
2. To find only emails with attachments, append `has:attachment` to the user's query before sending it to the API (transparent to the user).
3. Fetch message metadata (`format=metadata`) for the top results (fetch more than 3 to account for any edge cases, e.g. 10).
4. For each candidate message, call `users.messages.get` with `format=full` to inspect the `payload.parts` tree and collect attachment filenames.
5. Return the first 3 valid results ordered by `internalDate` descending (newest first — Gmail's default list order).

### Output
Plain-text output to stdout, one block per email:

```
[1] Subject: Re: Project files
    From: alice@example.com
    Date: 2026-05-25 14:32
    Attachments: report.pdf, budget.xlsx

[2] ...
```

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

### CLI interface
```
python gmail_search.py "your search query"
```
Query is a positional CLI argument. If omitted, the script prompts interactively.

**Assumption:** the script targets Python 3.8+.

## Alternative solutions considered

- **IMAP access:** Gmail supports IMAP, which avoids the Google Cloud Console setup. However, it requires enabling "Less secure app access" or App Passwords (the latter only for Workspace/legacy accounts), and the search capabilities are more limited than Gmail's native query syntax. Rejected in favour of the official API.
- **`simplegmail` / third-party wrappers:** lightweight but less maintained and still rely on the same OAuth flow underneath. No clear benefit over using the official client directly.

## Out of scope

- Downloading or saving attachment files.
- Pagination beyond the first page of results (the first page typically returns 100+ matches, so 3 results will always be available unless the mailbox has fewer).
- Support for multiple Gmail accounts simultaneously.
- GUI or web interface.
- Rate-limit handling / retry logic (acceptable for a simple script).

## Uncertainty

- **Number of API calls:** fetching `format=full` for each candidate is more expensive than `format=metadata`, but metadata alone does not reliably expose attachment filenames. If performance is a concern, `format=metadata` with `metadataHeaders` plus checking `payload.parts` for `mimeType != text/*` could reduce data transfer — but requires validation.
- **Shared/delegated mailboxes:** the script targets the authenticated user's own mailbox (`me`). Delegated access is not considered.
- **Query augmentation transparency:** appending `has:attachment` silently may surprise users who explicitly pass queries without it. The script should document this behaviour in its `--help` text.
