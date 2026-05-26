**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/02/compressed.md`

| Tier | Criterion | compressed |
|---|---|---|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +10 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 |
| **SHOULD** | Server-side result filtering | +3 |
| **SHOULD** | Server-side result count limit | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs (`token.json`… | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries (`google-ap… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.json… | +1 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- *Interactive query prompt as fallback* (Could, 0): The spec explicitly chooses usage message + exit 1 instead of an interactive fallback — the concept is absent, not contradicted, so 0 rather than negative.
- *`argparse` dependency* (Could, 0): Not mentioned; the spec lists pip packages but doesn't reference argparse specifically.
- *Server-side result count limit* (+3): "requesting up to 3 results" in the context of the API call clearly implies a server-side maxResults parameter rather than client-side truncation — treated as a full mention.
- *User having to download credentials.json* (+3): The spec says "user-provided" and points to Google Cloud Console as the source; the download step is implied rather than explicit, but substantively covered.

---

| Tier | compressed |
|---|---|
| Must (out of 6) | 6+ |
| Should (out of 8) | 8+ |
| Could (out of 8) | 6+ |
| Total points (92 max) | 90 |
| **Score** | **98%** |
