**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-outline-structure/01/compressed.md`

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
| **SHOULD** | Error handling for missing `credentials.json…` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `` `argparse` `` for CLI argument pars… | 0 |
| **COULD** | Excluding `` `credentials.json` `` and `` `token.json… `` | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

---

**Notes on non-obvious scores:**

- **Required setup steps (+5, partial):** The spec says "Requires a Google Cloud project with Gmail API enabled and `credentials.json` (OAuth client secret) in CWD," covering both enabling the API and the need for an OAuth client secret file. However, it never specifies that the credential type must be "Desktop App," which is a key distinction during setup.

- **Server-side result count limit (+2, partial):** The spec uses `maxResults=10` as a buffer and then selects the first 3 with confirmed attachments client-side. It demonstrates clear awareness of the `maxResults` API parameter, but the final count selection is done client-side — contrary to the criterion's intent of using the parameter as the definitive limit.

---

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1± |
| Could (out of 8) | 6+ |
| Total points (92 max) | 84 |
| **Score** | **91%** |
