**File mapping:** `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks/02/compressed.md`

| Tier | Criterion | compressed |
| ------------ | ----------------------------------------------- | ---------- |
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets … | +3 |
| **SHOULD** | Server-side result filtering (`has:attachmen… | +3 |
| **SHOULD** | Server-side result count limit (`maxResults`… | −3 |
| **SHOULD** | Error handling for missing `credentials.jso… | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope (`gmail.readonly` - mi… | +3 |
| **SHOULD** | Caching OAuth tokens across runs (`token.jso… | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 |
| **COULD** | Automatic token refresh on expiry | +1 |
| **COULD** | Interactive query prompt as fallback when no… | 0 |
| **COULD** | Dependencies: gmail API libraries (`google-a… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

**Notes on non-obvious scores:**

- **Must — Google Cloud Console setup (+5):** The spec covers "Google Cloud project created, Gmail API enabled, `credentials.json` downloaded" in its Assumptions section, addressing the API-enabling half. It does not explicitly describe "creating OAuth Desktop App credentials" as a discrete step — `credentials.json` is mentioned but its creation process is not explained. Half points.

- **Should — Server-side result count limit (−3):** The spec explicitly describes client-side truncation: "Fetch full metadata for each result until 3 are collected or results exhausted." This is the exact anti-pattern the criterion contrasts against (`maxResults` API parameter, not client-side truncation). Direct contradiction.

---

| Tier | compressed |
| --------------------- | ---------- |
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 7+ 1− |
| Could (out of 8) | 5+ |
| Total points (92 max) | 78 |
| **Score** | **85%** |
