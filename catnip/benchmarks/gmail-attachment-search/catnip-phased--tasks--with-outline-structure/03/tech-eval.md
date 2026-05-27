**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-outline-structure/03/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Consol… | +10 |
| **MUST** | Graceful handling when there are no results | +5 |
| **SHOULD** | User having to download OAuth client secrets … | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when n… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument par… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of… | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Graceful handling when there are no results (+5, half credit):** The spec says "note when fewer exist," which technically encompasses zero results, but the empty-result case is not addressed explicitly. Half credit awarded.
- **Required setup steps in Google Cloud Console (+10):** The spec names both prerequisites — "Gmail API enabled" and "OAuth 2.0 Desktop client" — under Setup & Dependencies. It doesn't use the phrase "Google Cloud Console" but substantively covers what needs to be done. Full credit awarded.
- **Interactive query prompt as fallback (0):** No mention anywhere; the spec only documents CLI argument input.
- **`argparse`, `.gitignore` exclusions (0):** Neither mentioned.

| Tier | compressed |
| --- | --- |
| Must (6) | 5+ 1± |
| Should (8) | 8+ |
| Could (8) | 5+ |
| Total points (92 max) | 84 |
| **Score** | **91%** |
