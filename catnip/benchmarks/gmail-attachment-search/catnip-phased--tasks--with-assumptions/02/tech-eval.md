**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-assumptions/02/compressed.md`

| Tier | Criterion | compressed |
|------|-----------|-----------|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
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
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Required setup steps (+5):** The spec covers enabling the Gmail API and obtaining `credentials.json` from the Google Cloud Console (framed as an Assumption), but never explicitly names the step of creating OAuth Desktop App credentials in the Console. Partial credit.
- **Server-side result count limit (+1):** The spec mentions `maxResults=10` as the API parameter, which is server-side, but then selects the first 3 client-side ("the first 3 are the target"). The criterion's key intent — using `maxResults` to avoid client-side truncation — is not met. Partial credit, rounded down.
- **Browser-based consent flow (+3):** The spec uses "OAuth 2.0 installed-app flow" (which is by definition browser-based) and explicitly names "browser consent" in the Uncertainty section. Combined with "token.json is written on first run," the full concept is addressed.

| Tier | compressed |
|------|-----------|
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1± |
| Could (out of 8) | 5+ |
| Total points (92 max) | 82 |
| **Score** | **89%** |
