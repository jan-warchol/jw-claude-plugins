**File mapping:**
- `compressed` → `catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks--with-assumptions/01/compressed.md`

---

| Tier | Criterion | compressed |
|------|-----------|------------|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 |
| **MUST** | CLI argument for search query | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 |
| **MUST** | Output per email: at least subject, sender, … | +10 |
| **MUST** | Required setup steps in Google Cloud Console… | +5 |
| **MUST** | Graceful handling when there are no results | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +2 |
| **SHOULD** | Server-side result filtering (`has:attachmen… | +3 |
| **SHOULD** | Server-side result count limit (`maxResults`… | +2 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 |
| **SHOULD** | API/network error handling | +3 |
| **SHOULD** | Read-only OAuth scope | +3 |
| **SHOULD** | Caching OAuth tokens across runs (`token.jso… | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 |
| **COULD** | Automatic token refresh on expiry | 0 |
| **COULD** | Interactive query prompt as fallback when no… | +1 |
| **COULD** | Dependencies: gmail API libraries (`google-a… | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso… | 0 |
| **COULD** | Attachment downloading as explicitly out of … | +1 |
| **COULD** | Pagination as explicitly out of scope | 0 |
| **COULD** | Multiple Gmail accounts as explicitly out of… | +1 |

---

**Notes on non-obvious scores:**

- **Required setup steps (MUST, +5):** The spec acknowledges the need via an error handler that links to Google Cloud Console setup and an explicit assumption that the user has `credentials.json`. However, it never describes the actual steps (enabling the API, creating an OAuth Desktop App credential). Partial credit.

- **credentials.json download (SHOULD, +2):** The assumption section says "user has a Google Cloud project and `credentials.json`" and error handling covers the missing-file case, both showing awareness that the file is needed. But the spec frames it as something already done rather than a step the user must take. Partial credit.

- **maxResults API parameter (SHOULD, +2):** The spec does use `maxResults=10` (a server-side page size parameter) and paginates via `nextPageToken`, so it avoids naive client-side truncation from an unbounded download. However, the actual 3-result cap is enforced client-side after fetching page(s), so it doesn't fully match the criterion's intent of using `maxResults` to bound the result count server-side. Partial credit.

- **Attachment downloading out of scope (COULD, +1):** The Constraints section says "no body/attachment data stored to disk" and "no operations beyond search + display," which explicitly covers this. Full credit.

- **Pagination out of scope (COULD, 0):** The spec actually uses pagination (`nextPageToken`) as part of its solution — it does not declare pagination out of scope.

---

| Tier | compressed |
|------|------------|
| Must (out of 6) | 5+ 1± |
| Should (out of 8) | 6+ 2± |
| Could (out of 8) | 4+ |
| Total points (92 max) | 81 |
| **Score** | **88%** |
