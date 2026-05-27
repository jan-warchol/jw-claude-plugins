**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/03/compressed.md`

| Tier | Criterion | compressed |
|---|---|---|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Consol… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secret… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | -3 |
| **SHOULD** | Error handling for missing `credentials.jso…` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first r… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when n… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument par… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of… | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out o… | +1 |

**Notes on non-obvious scores:**

- **Must / Google Cloud Console setup (+5):** The spec mentions "user has a Google Cloud project with Gmail API enabled" as an assumption and references `credentials.json` from Google Cloud Console, but does not describe the required user actions (enabling the API, creating OAuth Desktop App credentials) as explicit setup steps the reader must take. Partial credit.
- **Should / Server-side result count limit (−3):** The criterion calls for using the `maxResults` API parameter rather than client-side truncation. The spec explicitly uses client-side truncation ("Stop after collecting 3"), which contradicts this criterion.

| Tier | compressed |
|---|---|
| Must (6) | 5+ 1± |
| Should (8) | 7+ 1- |
| Could (8) | 5+ |
| Total points (92 max) | 78 |
| **Score** | **85%** |
