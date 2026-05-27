**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/01/compressed.md`

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
| **SHOULD** | Server-side result filtering `has:attachment… | 0 |
| **SHOULD** | Server-side result count limit `maxResults` … | 0 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | -1 |
| **COULD** | Dependencies: gmail API libraries `google-ap… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.json… | +1 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Required setup steps (+5):** The spec mentions creating a GCP project, enabling the Gmail API, and that `credentials.json` comes from Google Cloud Console — but never explicitly describes *creating* the OAuth Desktop App credential type in the Console. Enabling the API is clearly stated; the credential-creation step is only implied by "user-provided" and "OAuth client secrets from Google Cloud Console."
- **Server-side filtering (0):** The spec uses client-side attachment detection (checking `filename` field on message parts) rather than appending `has:attachment` server-side. The approach is different but the spec never explicitly says it won't use server-side filtering, so scored 0 rather than negative.
- **Server-side count limit (0):** The spec uses a client-side 500-message cap rather than the `maxResults` API parameter. Same reasoning as above — scored 0.
- **Interactive query prompt (-1):** Contradicted — the spec explicitly handles the no-argument case by printing a usage hint and exiting with code 1, the opposite of an interactive fallback.

---

| Tier | compressed |
| --- | --- |
| Must (6 criteria) | 5+ 1± |
| Should (8 criteria) | 6+ |
| Could (8 criteria) | 6+ 1- |
| Total points (92 max) | 78 |
| **Score** | **85%** |
