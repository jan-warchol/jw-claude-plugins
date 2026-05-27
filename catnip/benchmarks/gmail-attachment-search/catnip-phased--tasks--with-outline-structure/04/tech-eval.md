**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-outline-structure/04/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Consol… | +10 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.jso…` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | 0 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument par… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of… | 0 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes:**
- **Read-only OAuth scope (0):** The spec never mentions `gmail.readonly` or any OAuth scope. While the Must-not list prohibits writes, no scope is specified for the OAuth configuration.
- **Server-side result count limit (+3):** The spec uses `maxResults=20` as an API-side parameter rather than fetching all results and truncating client-side — consistent with the criterion's intent.
- **`argparse` dependency (0):** CLI parsing is implied but argparse is never named.
- **Attachment downloading / version control exclusions (0):** Neither is mentioned in the spec.

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 6+ |
| Should (out of 8) | 7+ |
| Could (out of 8) | 5+ |
| Total points (92 max) | 86 |
| **Score** | **93%** |
