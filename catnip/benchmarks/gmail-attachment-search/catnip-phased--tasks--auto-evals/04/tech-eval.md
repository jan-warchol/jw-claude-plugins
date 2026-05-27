**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/01/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +10 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | −3 |
| **SHOULD** | Server-side result count limit | −3 |
| **SHOULD** | Error handling for missing `credentials.json` | +1 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | −1 |
| **COULD** | Excluding `credentials.json` and `token.json… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Server-side result filtering (−3):** The spec explicitly opts out — "no automatic `has:attachment` appended" — contradicting the criterion.
- **Server-side result count limit (−3):** The spec uses client-side pagination (stop paginating after 3 matching messages are found), which is the opposite of using a `maxResults` API parameter.
- **Error handling for missing `credentials.json` (+1):** The spec lists "Print error, exit 1" but says nothing about the message including setup instructions. Partial credit — the mechanism is there, the guidance content is absent.
- **`argparse` (−1):** The spec explicitly rejects argparse ("a single positional arg warrants no argparse"), directly contradicting the criterion.

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 6+ |
| Should (out of 8) | 5+ 1± 2− |
| Could (out of 8) | 5+ 1− |
| Total points (92 max) | 74 |
| **Score** | **80%** |
