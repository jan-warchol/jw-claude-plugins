**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/02/compressed.md`

| Tier | Criterion | compressed |
|---|---|---|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | -3 |
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
| **COULD** | Excluding `credentials.json` and `token.jso…` | +1 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Required setup steps (Must, +5):** The spec mentions that `credentials.json` comes from Google Cloud Console and handles the missing-file case, but never describes the actual setup steps (enabling the Gmail API, creating an OAuth Desktop App credential). Half credit.
- **Server-side result filtering (Should, -3):** The spec explicitly states `has:attachment` is *not* appended to the query — directly contradicting the criterion. Negative full points.
- **Server-side result count limit (Should, +3):** "request up to 100 results" describes the `maxResults` API parameter; the 3-result cap is a separate client-side filter. Criterion satisfied.

| Tier | compressed |
|---|---|
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1- |
| Could (out of 8) | 6+ |
| Total points (92 max) | 79 |
| **Score** | **86%** |
