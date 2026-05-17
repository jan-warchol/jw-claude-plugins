# Key Points

## Must mention

- OAuth 2.0 authentication with Gmail API
- CLI argument for search query
- 3 most recent matching emails as the result
- Output per email: at least subject, sender, and attachment filenames (all are absolutely
  necessary)
- Required setup steps in Google Cloud Console: enabling API, creating OAuth Desktop App credentials
- Graceful handling when there are no results (informative message, no crash)

## Should mention

- User having to download OAuth client secrets file (`credentials.json`)
- Server-side result filtering (`has:attachment` appended to user query at the API level)
- Server-side result count limit (`maxResults` API parameter, not client-side truncation)
- Error handling for missing `credentials.json` (message with setup instructions)
- API/network error handling (catch `HttpError`, print message)
- Read-only OAuth scope (`gmail.readonly` - minimum privilege)
- Caching OAuth tokens across runs (`token.json` file)
- Browser-based OAuth consent flow on first run

## Could mention

- Automatic token refresh on expiry
- Interactive query prompt as fallback when no CLI argument is given
- Dependencies: gmail API libraries (`google-api-python-client` and `google-auth-oauthlib`)
- Dependency: `argparse` for CLI argument parsing
- Excluding `credentials.json` and `token.json` from version control
- Attachment downloading as explicitly out of scope
- Pagination as explicitly out of scope
- Multiple Gmail accounts as explicitly out of scope

## Should not mention

## Must not mention
