# Gmail Attachment Search Script

## Goal

A CLI Python script that accepts a Gmail search query, finds the three most recent matching emails
that have attachments, and prints their metadata to stdout.

## Behavior

### Invocation

```
python search_gmail.py "<query>"
```

The query uses Gmail's native search syntax (e.g. `from:alice subject:invoice`).

### Output

For each matching email (up to 3, ordered newest-first), print:

- Subject
- Sender
- Date
- List of attachment filenames

If fewer than 3 matches exist, return however many are found with no error.

If no matches exist, print a clear message and exit 0.

### Error handling

Exit with a non-zero code and a human-readable message on authentication failure or API error.

## Solution

### Authentication

Use the Gmail API with OAuth2. On first run, open a browser for the OAuth consent flow and cache
the token in `token.json`. Subsequent runs use the cached token, refreshing automatically.
Credentials are loaded from `credentials.json` in the working directory.

### Search strategy

Append `has:attachment` to the user query before sending to the Gmail API `users.messages.list`
endpoint. Retrieve at most 3 results, sorted by date descending (default Gmail API order).

### Dependencies

`google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

### Rejected alternatives

IMAP with app password — rejected in favour of OAuth2 for security and alignment with Google's
recommended approach.

## Unknowns

- Required OAuth scopes: `gmail.readonly` should suffice; confirm no broader scope is needed.
- Behaviour when an attachment has no filename (inline image with Content-ID only) — omit or label
  as `<unnamed>`.
