**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-outline-structure/02/compressed.md`

| Tier | Criterion | compressed |
|---|---|---|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets … | +3 |
| **SHOULD** | Server-side result filtering | +1 |
| **SHOULD** | Server-side result count limit | −3 |
| **SHOULD** | Error handling for missing `credentials.json` | +2 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | 0 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | +1 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of s… | +1 |
| **COULD** | Pagination as explicitly out of scope | 0 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Must #5 (+5):** Spec mentions "Gmail API enabled" and "credentials.json from the Cloud Console" but never specifies creating an OAuth Desktop App client type — a concrete required step.
- **Should #2 (+1):** Spec says adding `has:attachment` is "recommended to pre-filter server-side," framing it as user guidance rather than an automatic script-applied filter.
- **Should #3 (−3):** Spec explicitly describes client-side truncation ("Fetch pages and stop at 3 qualifying messages"), directly contradicting the criterion calling for the `maxResults` API parameter approach.
- **Should #4 (+2):** Spec confirms a clear error on missing `credentials.json` but says nothing about including setup instructions in that error message.

| Tier | compressed |
|---|---|
| Must (6) | 5+ 1± |
| Should (8) | 5+ 2± 1− |
| Could (8) | 5+ |
| Total points (92 max) | 75 |
| **Score** | **82%** |
