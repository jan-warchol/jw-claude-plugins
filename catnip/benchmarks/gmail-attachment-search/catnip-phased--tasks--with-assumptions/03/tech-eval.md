**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-assumptions/03/compressed.md`

| Tier | Criterion | compressed |
|---|---|---|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +10 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of… | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes:**
- **API/network error handling (+3):** The parenthetical names `HttpError` as a clarifying detail; the spec covers the concept substantively (HTTP status + message → stderr, exit 1) without naming the specific exception class. Full points awarded.

---

| Tier | compressed |
|---|---|
| Must (out of 6) | 6+ |
| Should (out of 8) | 8+ |
| Could (out of 8) | 5+ |
| Total points (92 max) | 89 |
| **Score** | **97%** |
