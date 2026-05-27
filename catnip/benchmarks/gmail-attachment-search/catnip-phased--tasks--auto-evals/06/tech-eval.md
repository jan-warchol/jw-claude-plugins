**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/03/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Consol… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secret… | +3 |
| **SHOULD** | Server-side result filtering | 0 |
| **SHOULD** | Server-side result count limit | +1 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.json… | +1 |
| **COULD** | Attachment downloading as explicitly out of… | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Must — Required setup steps (+5):** The spec mentions `credentials.json` "from Google Cloud Console" and that the client must be an "installed-application" type, which partially covers the GCC credential creation step. However, it never mentions enabling the Gmail API in Cloud Console as a required setup step. Half credit.
- **Should — Server-side result filtering (0):** The spec explicitly states the user query is "passed directly to the Gmail API `q` parameter" with no mention of appending `has:attachment`. Attachment detection is done entirely client-side by walking the MIME tree. The criterion's concept is absent.
- **Should — Server-side result count limit (+1):** The spec says "fetch up to 100 results" in the context of the `users.messages.list` call, implying a server-side limit, but doesn't explicitly call it the `maxResults` API parameter or contrast it with client-side truncation. Partial credit.

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 6+ 1± |
| Could (out of 8) | 6+ |
| Total points (92 max) | 80 |
| **Score** | **87%** |
