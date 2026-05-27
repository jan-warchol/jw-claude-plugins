**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-outline-structure/05/compressed.md`

| Tier | Criterion | compressed |
|------|-----------|------------|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Consol… | +10 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering (`has:attachmen… | +3 |
| **SHOULD** | Server-side result count limit | -3 |
| **SHOULD** | Error handling for missing `credentials.json` | +1 |
| **SHOULD** | API/network error handling | +2 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | 0 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries (`google-a… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.json… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | 0 |

**Notes on non-obvious scores:**

- **Server-side result count limit (-3):** The spec explicitly describes client-side truncation — it fetches the first page at the API default of 100 results and then selects "the first 3 IDs" client-side. This directly contradicts the criterion's expectation of using the `maxResults` API parameter for server-side limiting.
- **Error handling for missing `credentials.json` (+1):** The spec broadly covers "Exit non-zero with a readable message on auth or API errors" but does not call out the missing-`credentials.json` case specifically, nor mention that the error message should include setup instructions.
- **API/network error handling (+2):** The same general auth/API error clause addresses the concept, but `HttpError` is not named; most of the concept is present, one key element is missing.
- **Dependencies (+1):** Both `google-api-python-client` and `google-auth-oauthlib` are listed explicitly, satisfying the criterion.

---

| Tier | compressed |
|---|---|
| Must (out of 6) | 6+ |
| Should (out of 8) | 5+ 2± 1- |
| Could (out of 8) | 3+ |
| Total points (92 max) | 78 |
| **Score** | **85%** |
