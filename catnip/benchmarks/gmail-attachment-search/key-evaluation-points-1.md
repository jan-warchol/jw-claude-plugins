# Key Points

<!-- Weights: must=5, should=3, could=1, must-not=-3 -->

## Must (weight: 5)
- CLI argument for search query
- `has:attachment` appended to user query at the API level (server-side filtering, not client-side)
- Result count: 3 most recent matching emails
- Per-email output fields: subject, sender (From), date, attachment filenames
- OAuth 2.0 authentication with Gmail API

## Should (weight: 3)
- Graceful handling when fewer than 3 results exist (informative message, no crash)
- Read-only OAuth scope (`gmail.readonly`)
- Gmail API libraries (`google-api-python-client` + `google-auth-oauthlib`)
- `credentials.json` as OAuth client secrets file
- `token.json` for caching OAuth token across runs
- Browser-based OAuth consent flow on first run
- Automatic token refresh on expiry
- `requirements.txt` for dependency declaration
- Missing `credentials.json`: clear error message + exit with non-zero code
- API/network errors: surface error message to user + exit with non-zero code
- No-results case: informative message + exit 0

## Could (weight: 1)
- `.gitignore` for `credentials.json` and `token.json`
- Interactive query prompt as fallback when no CLI argument is given
- Google Cloud Console setup instructions included in script or docs
- Downloading attachment content explicitly listed as out of scope
- Pagination explicitly listed as out of scope
- Multiple Gmail accounts explicitly listed as out of scope
- Sending or modifying emails explicitly listed as out of scope

## Must Not (weight: -3)
