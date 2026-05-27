**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-outline-structure/06/compressed.md`

---

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender,… | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +10 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `argparse` for CLI argument par… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 |
| **COULD** | Attachment downloading as explicitly out of… | +1 |
| **COULD** | Pagination as explicitly out of scope | 0 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

---

**Notes on non-obvious scores:**

- **Server-side result count limit (+3):** The spec uses `maxResults=20` via the API, then collects attachment-bearing results up to 3 client-side. This is not "client-side truncation" in the sense the criterion warns against — it's legitimate candidate fetching with attachment filtering. Full credit given.
- **Pagination as explicitly out of scope (0):** The spec implements up to 3 pages of pagination and only puts "Pagination beyond 3 pages" out of scope. The criterion expects pagination to be entirely out of scope. Score 0.

---

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 6+ |
| Should (out of 8) | 8+ |
| Could (out of 8) | 4+ |
| Total points (92 max) | 88 |
| **Score** | **96%** |
