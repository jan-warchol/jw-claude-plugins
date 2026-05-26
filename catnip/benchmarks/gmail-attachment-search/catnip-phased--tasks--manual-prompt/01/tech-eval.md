**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/01/compressed.md`

| Tier | Criterion | compressed |
|------|-----------|------------|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets … | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | -3 |
| **SHOULD** | Error handling for missing `credentials.jso…` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | 0 |

**Notes on non-obvious scores:**

- **Required setup steps (GCC) — +5:** The spec acknowledges API enablement ("GCP project with Gmail API enabled") and that `credentials.json` comes from Google Cloud Console, but never specifies creating an *OAuth Desktop App* credential type. Half credit.
- **Server-side result count limit — -3:** The spec explicitly describes client-side truncation ("Take the first three message IDs" from the default 500-result page), directly contradicting the criterion's expectation of using the `maxResults` API parameter.

---

| Tier | compressed |
|------|------------|
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1- |
| Could (out of 8) | 4+ |
| Total points (92 max) | 77 |
| **Score** | **84%** |
