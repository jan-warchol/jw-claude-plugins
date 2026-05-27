# Gmail Attachment Search — Spec

## Objective

CLI Python script: accepts a search query, searches Gmail via the API, prints the 3 most recent matching emails with attachments (subject, sender, date, filenames). Goal: quickly surface attachment emails for automation or personal use without a browser.

---

## Requirements

### Must do
- Accept `query` as a CLI argument; prompt interactively if omitted.
- Authenticate via OAuth 2.0 (Gmail API, readonly scope).
- Search Gmail with the provided query and filter to emails with attachments.
- Print up to 3 results (subject, sender, date, attachment filenames); if fewer than 3 exist, print what's found with a count note.
- Exit with a clear error on: missing `credentials.json`, auth failure, network error, or zero results.

### Must not do
- Download or save attachments (metadata only).
- Modify, delete, or send emails.
- Store credentials beyond OAuth requirements.

---

## Solution

### Dependencies
- `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

### Authentication and setup
Requires a Google Cloud project with Gmail API enabled and `credentials.json` from the Cloud Console (manual prerequisite; script errors clearly if absent). On first run, opens a browser for OAuth consent (scope: `gmail.readonly`) and caches the token in `token.json`. To re-authenticate after revocation, delete `token.json`.

### CLI interface
`argparse` with a single positional `query`; multi-word queries need shell quoting:
```
python gmail_search.py "invoice from:supplier@example.com"
```
Falls back to `input("Search query: ")` if omitted.

### Search and filtering
Pass the query directly to `users.messages.list` (Gmail search syntax: `from:`, `has:attachment`, etc.; results newest-first). Adding `has:attachment` to the query is recommended to pre-filter server-side; the script still verifies client-side since Gmail can mark inline images as attachments with no filename.

Per candidate message, call `users.messages.get` (`format=metadata`) and **recursively** walk `parts`, collecting entries with a non-empty `filename`. Fetch pages and stop at 3 qualifying messages.

### Output
```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date>
    Files:   <filename1>, <filename2>, …
Found 3 result(s).
```
Fewer than 3: `Found N result(s) (fewer than 3 matched).`
Zero: `No emails matching "<query>" with attachments were found.`

---

## Alternatives considered

- **IMAP**: No Google API setup, but needs app passwords, weaker search, and complex MIME parsing.
- **`simplegmail` / wrappers**: Less boilerplate but opaque extra dependency; not justified.

---

## Out of scope

Saving attachments · fetching >3 results · multiple accounts · email body/labels · GUI · tests

---

## Known limitations

Iterating many pages to find 3 attachment emails may hit API quotas on large accounts. No retry logic planned.
