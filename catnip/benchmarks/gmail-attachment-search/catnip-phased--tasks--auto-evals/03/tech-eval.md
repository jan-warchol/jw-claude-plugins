**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/03/compressed.md`

| Tier | Criterion | compressed |
| --- | --- | --- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sende… | +10 |
| **MUST** | Required setup steps in Google Cloud Cons… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secr… | +3 |
| **SHOULD** | Server-side result filtering | −3 |
| **SHOULD** | Server-side result count limit | −3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when… | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 |
| **COULD** | Dependency: `` `argparse` `` for CLI argument p… | 0 |
| **COULD** | Excluding `` `credentials.json` `` and `` `token.j…` `` | 0 |
| **COULD** | Attachment downloading as explicitly out … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out… | +1 |

**Notes on non-obvious scores:**

- **Required setup steps (+5, partial):** The spec mentions enabling the Gmail API and downloading `credentials.json` from Google Cloud Console, but never specifies creating an *OAuth Desktop App* credential type — a required step that distinguishes it from other credential types. Half credit.
- **Server-side result filtering (−3, contradicted):** The spec explicitly states the opposite design: "No `has:attachment` auto-append: the query is passed through unchanged; filtering happens in code."
- **Server-side result count limit (−3, contradicted):** The criterion expects `maxResults` to be used as the 3-result cap. The spec uses `maxResults=20` as a batch size, then applies client-side counting to find 3 qualifying messages — the exact anti-pattern the criterion flags.

---

| Tier | compressed |
| --- | --- |
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 6+ 2− |
| Could (out of 8) | 5+ |
| Total points (92 max) | 72 |
| **Score** | **78%** |
