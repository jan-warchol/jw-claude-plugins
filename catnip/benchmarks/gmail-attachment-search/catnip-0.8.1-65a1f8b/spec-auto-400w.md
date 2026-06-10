# Gmail Attachment Search — Specification

## Goal

A single-file Python CLI script that accepts a Gmail search query, finds the 3 most recent
matching emails that have attachments, and prints a summary of each to stdout.

## Behavior

### Invocation

```
python search_attachments.py "<gmail query>"
```

The query is a standard Gmail search string (e.g. `"from:alice subject:invoice"`). The script
appends `has:attachment` automatically so the user does not need to include it.

### Output

For each matching email (up to 3, newest first), print:

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <received date, human-readable>
    Files:   <comma-separated attachment filenames>
```

If 0–2 matches are found, print however many exist without warning or error.

### Authentication

On first run, open a browser for the Gmail OAuth2 consent flow. Store the resulting token in
`token.json` in the working directory. On subsequent runs, load the token silently and refresh it
if expired. A `credentials.json` file (OAuth2 client secret, downloaded from Google Cloud Console)
must be present in the working directory.

### Error cases

- Missing `credentials.json`: print a clear message explaining where to obtain it and exit 1.
- Auth failure / token unrefreshable: delete `token.json`, print a message asking user to re-run,
  exit 1.
- Gmail API error: print the error and exit 1.

## Solution

### Dependencies

- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`

### Implementation

1. Load `credentials.json`; run OAuth2 installed-app flow if `token.json` is absent or invalid.
   Request only the `gmail.readonly` scope.
2. Call `users.messages.list` with query `<user_query> has:attachment`, `maxResults=3`. Gmail
   returns results newest-first by default.
3. For each message ID, call `users.messages.get` with `format=metadata`, requesting headers
   `Subject`, `From`, `Date` and `parts` to extract attachment filenames (parts where `filename`
   is non-empty).
4. Print the formatted summary.

### Key design choices

- Append `has:attachment` server-side rather than filtering client-side: avoids fetching extra
  pages of results.
- `gmail.readonly` scope only: minimises OAuth permission footprint.
- `format=metadata` (not `full`): avoids downloading message bodies and attachment data.
- No dependency beyond the official Google client libraries.

## Unknowns

- Multipart nested MIME structures (e.g. `multipart/mixed` inside `multipart/related`) may require
  recursive part traversal to find all attachment filenames; the implementation should handle at
  least one level of nesting.
- Gmail API quota limits (default 250 quota units/second, 1 unit per `messages.get`) are not a
  concern for 3 requests but should be noted if the limit is later raised.
