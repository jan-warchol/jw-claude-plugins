**File reference:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-assumptions-no-reorganize/03/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | −3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries (`google-a… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.json… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | 0 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**
- **Required setup steps (+5):** The spec mentions a Google Cloud project, enabling the Gmail API, and downloading `credentials.json`, but never specifies creating an "OAuth Desktop App" credential type — only that `credentials.json` comes from Google Cloud Console.
- **Server-side result count limit (−3):** The criterion calls for `maxResults` (server-side limiting); the spec explicitly uses client-side counting ("paginate until 3 matches found"), which is the exact approach the parenthetical flags as *not* the right one — a direct contradiction.

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1− |
| Could (out of 8) | 5+ |
| Total points (92 max) | 78 |
| **Score** | **85%** |
