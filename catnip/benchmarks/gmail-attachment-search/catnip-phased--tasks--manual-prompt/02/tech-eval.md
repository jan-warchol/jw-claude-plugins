**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/02/compressed.md`

---

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +2 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument par… | 0 |
| **COULD** | Excluding `credentials.json` and `token.json… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Required setup steps (+5, partial):** The spec mentions `credentials.json` is a "Desktop app OAuth2 client from Google Cloud Console" (covering credential creation) and lists "Gmail API enabled" as an assumption. Neither step is framed as an instruction to the reader — they appear as background prerequisites rather than required setup guidance.

- **Server-side result count limit (+2, partial):** The spec describes "up to 10 results per page" within the API call step, implying `maxResults=10` server-side. The concept is present but `maxResults` is never named, and the distinction from client-side truncation is not drawn.

---

| Tier | compressed |
| --- | --- |
| Must (6) | 5+ 1± |
| Should (8) | 7+ 1± |
| Could (8) | 5+ |
| Total points (92 max) | 83 |
| **Score** | **90%** |
