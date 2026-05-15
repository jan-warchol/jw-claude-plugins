# Key Points

<!-- Weights: must=5, should=3, could=1, must-not=-3 -->

## Must mention (weight: 5)
- CLI query string as required input
- `has:attachment` appended to user query at the API level (server-side filtering, not client-side post-filtering)
- 3 most recent matching emails as the result limit
- Output per email: subject, sender, date, and attachment filenames
- OAuth 2.0 authentication
- `credentials.json` as the OAuth client secrets file
- `token.json` for token caching across runs
- `gmail.readonly` OAuth scope (read-only, minimum privilege)

## Should mention (weight: 3)
- `google-api-python-client` and `google-auth-oauthlib` as the Gmail API libraries
- Browser-based OAuth consent flow on first run
- Result count limit via `maxResults` API parameter (not client-side truncation)
- `messages.get` to extract headers and MIME part filenames per message
- Missing `credentials.json`: clear error message with setup instructions, exit code 1
- API/network error handling (catch `HttpError`, print message, exit)
- No-results case: informative message, exit code 0
- `credentials.json` and `token.json` excluded from version control

## Could mention (weight: 1)
- `requirements.txt` listing the Google packages
- Interactive prompt fallback when no CLI argument is provided
- `argparse` for CLI argument parsing
- Google Cloud Console setup as a manual prerequisite (enable API, create OAuth Desktop App credentials)
- Token refresh handled automatically by `google-auth` (no re-auth needed for expired tokens)
- Attachment downloading as explicitly out of scope
- Pagination as explicitly out of scope
- Multiple Gmail accounts as explicitly out of scope

## Must Not mention (weight: -3)
