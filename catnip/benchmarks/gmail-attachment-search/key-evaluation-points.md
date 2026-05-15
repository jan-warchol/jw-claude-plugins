# Key Points

## Must mention (weight: 5)
- OAuth 2.0 authentication with Gmail API
- CLI query string as required input
- 3 most recent matching emails as the result limit
- Output per email: at least subject, sender, and attachment filenames
- `has:attachment` appended to user query at the API level (server-side filtering, not client-side post-filtering)
- Result count limit via `maxResults` API parameter (not client-side truncation)
- `credentials.json` as the OAuth client secrets file

## Should mention (weight: 3)
- `token.json` for token caching across runs
- Read-only OAuth scope (`gmail.readonly` - minimum privilege)
- Browser-based OAuth consent flow on first run
- `messages.get` to extract headers and MIME part filenames per message
- Missing `credentials.json`: clear error message with setup instructions, exit code 1
- Error handling for missing `credentials.json`
- API/network error handling (catch `HttpError`, print message)
- Graceful handling when fewer than 3 results exist (informative message, no crash)
- Google Cloud Console setup as a manual prerequisite (enable API, create OAuth Desktop App credentials, downloading the file)

## Could mention (weight: 1)
- Gmail API libraries (`google-api-python-client` and `google-auth-oauthlib`)
- `credentials.json` and `token.json` excluded from version control
- `requirements.txt` listing dependencies
- Interactive prompt fallback when no CLI argument is provided
- `argparse` for CLI argument parsing
- Token refresh handled automatically by `google-auth` (no re-auth needed for expired tokens)
- Attachment downloading as explicitly out of scope
- Pagination as explicitly out of scope
- Multiple Gmail accounts as explicitly out of scope
- Using `format=metadata` with `metadataHeaders=["Subject","From","Date"]` to avoid the overhead of fetching whole emails.

## Must Not mention (weight: -3)
