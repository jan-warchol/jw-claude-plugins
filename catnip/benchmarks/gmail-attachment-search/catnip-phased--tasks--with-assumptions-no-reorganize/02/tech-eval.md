**File mapping:**
- `compressed`: `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-assumptions-no-reorganize/02/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets … | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | 0 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries (`google-a… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes:**

- **Required setup steps (+5, partial):** The spec covers the setup steps in an Assumption block ("create project, enable Gmail API, download credentials") rather than as explicit instructions, and does not specify that credentials must be of type "OAuth Desktop App" — a key element, since other credential types (API keys, web app credentials) won't work for this flow.
- **Read-only OAuth scope (0):** The spec does not mention `gmail.readonly` or any OAuth scope at all.

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ |
| Could (out of 8) | 6+ |
| Total points (92 max) | 82 |
| **Score** | **89%** |
