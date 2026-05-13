# Key Points

## Must mention
- OAuth 2.0 authentication with Gmail API
- CLI argument for search query
- 3 most recent matching emails as the result
- Output per email: at least subject, sender, and attachment filenames
- Required setup in Google Cloud Console (enabling API, creating OAuth Desktop App credentials)

## Should mention
- Downloading OAuth client secrets file (`credentials.json`)
- Server-side result filtering (`has:attachment` appended to user query at the API level)
- Server-side result count limit (`maxResults` API parameter, not client-side truncation)
- Error handling for missing `credentials.json` (message with setup instructions)
- API/network error handling (catch `HttpError`, print message)
- Graceful handling when fewer than 3 emails match (informative message, no crash)
- Read-only OAuth scope (`gmail.readonly` - minimum privilege)
- Caching OAuth tokens across runs (`token.json` file)
- Browser-based OAuth consent flow on first run
- Automatic token refresh on expiry

## Could mention
- Interactive query prompt as fallback when no CLI argument is given
- Avoiding the overhead of fetching whole emails (using `messages.get` with `format=metadata` and `metadataHeaders`)
- Dependencies: gmail API libraries (`google-api-python-client` and `google-auth-oauthlib`)
- Dependency: `argparse` for CLI argument parsing
- Excluding `credentials.json` and `token.json` from version control
- Attachment downloading as explicitly out of scope
- Pagination as explicitly out of scope
- Multiple Gmail accounts as explicitly out of scope

## Should not mention

## Must not mention
