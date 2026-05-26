**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/03/compressed.md`

| Tier | Criterion | compressed |
|------|-----------|-----------|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets … | +1 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | +1 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **MUST — Setup steps (+5, partial):** The spec covers enabling the API and creating an OAuth client ID (`credentials.json`), but never specifies the credential type must be "Desktop App". That is the critical detail a user needs when navigating Google Cloud Console.
- **SHOULD — Download `credentials.json` (+1, partial):** The spec lists `credentials.json` as a prerequisite and a file not committed to VCS, but never says the user must download it from Google Cloud Console. The file's existence is implied, but the download action is absent.
- **SHOULD — API/network error handling (+3, full):** The spec says "API error (4xx/5xx): surface message, exit non-zero" — this covers the concept even though `HttpError` (the parenthetical clarification) is not named explicitly.

| Tier | compressed |
|------|-----------|
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1± |
| Could (out of 8) | 7+ |
| Total points (92 max) | 84 |
| **Score** | **91%** |
