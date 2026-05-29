# Reference Spec Evaluation Report

Specs evaluated:

- `condensed-1400` → `condensed-1400-words.md`
- `condensed-500` → `condensed-500-words.md`

Criteria file: `tech-criteria.md`

---

## Structural Evaluation

### Topics

| Topic              | condensed-1400 | condensed-500 |
| ------------------ | -------------- | ------------- |
| Goal               | 3              | 3             |
| Requirements       | 3              | 3             |
| Solution           | 4              | 3             |
| Out of scope       | 3              | 3             |
| Uncertainty        | 2              | 1             |
| **Total (max 17)** | **15**         | **13**        |

**Notes:**

- **Solution — condensed-1400 (4):** Gets +2 (not +1) because the architecture section explicitly
  states both the decision and its trade-off: _"Trade-off accepted: cleaner React story, harder to
  expose a clean imperative non-React API."_ WebGL and OffscreenCanvas/Workers are discussed with
  explicit rejection reasons (+1 alternatives, +1 trade-offs).
- **Solution — condensed-500 (3):** Architecture is present but the trade-off reasoning was dropped
  in compression ("Clean imperative non-React API and CSS-variable theming: later" is a deferral,
  not an explanation), so only +1 for solution. Still earns +1 trade-offs and +1 alternatives.
- **Uncertainty — condensed-1400 (2):** +1 for risks (highlights degenerate when highlighted set ≫
  total — "accepted"; canvas allocation failure handling; time labels best-effort). +1 for open
  questions scattered throughout (reversed-range behavior TBD, React `ref` API TBD, tooltip may
  split into separate component). No dedicated section, no explicit assumptions list.
- **Uncertainty — condensed-500 (1):** Risks are barely touched ("assumes highlighted ≪ total";
  WebGL/OffscreenCanvas trade-offs). Open questions were stripped out entirely. No dedicated
  section.

### Metrics

| Metric               | condensed-1400 | condensed-500 |
| -------------------- | -------------- | ------------- |
| Word count           | 1 236          | 463           |
| Avg section length   | 86.6           | 36.9          |
| Avg paragraph length | 63.7           | 34.1          |
| Avg bullet length    | 13.3           | 9.7           |
| Code snippets ratio  | 1%             | 2%            |

---

## Technical Evaluation

### Criteria scores

| Tier       | Criterion                                      | condensed-1400 | condensed-500 |
| ---------- | ---------------------------------------------- | -------------- | ------------- |
| **MUST**   | Canvas-based, performance-focused library for… | +10            | +10           |
| **MUST**   | Performance target ≥ uPlot, benchmarked with…  | +10            | +10           |
| **MUST**   | Independent X values per series                | +10            | +10           |
| **MUST**   | Log scale as a special case of symlog          | +10            | +10           |
| **MUST**   | Shared zoom+highlight reactive-only — does N…  | +10            | +10           |
| **MUST**   | Path2D cache stored in zoom-normalized data …  | +10            | +10           |
| **MUST**   | Stable series ids as cache keys                | +10            | +10           |
| **MUST**   | Data normalization to handle ranges where max… | +10            | +10           |
| **SHOULD** | Canonical use case: ML training metrics dash…  | +3             | +3            |
| **SHOULD** | Main benchmark: 100k points per chart          | +3             | +3            |
| **SHOULD** | Concrete FPS benchmark scenarios               | +3             | +3            |
| **SHOULD** | Symlog parametrization auto-derived from data… | +3             | +3            |
| **SHOULD** | Tick placement must match displayed label pre… | +3             | +3            |
| **SHOULD** | Auto-fit Y stays active under X-zoom; can onl… | +3             | +3            |
| **SHOULD** | Hover highlight: interpolated y at hovered x…  | +3             | +3            |
| **SHOULD** | NaN/missing values: skip and connect across    | +3             | +3            |
| **SHOULD** | Canvas stacking; highlighted marks drawn twic… | +3             | +3            |
| **SHOULD** | Framework-agnostic core with thin declarativ…  | +3             | +3            |
| **SHOULD** | Input formats: number[], Float32Array, Float…  | +3             | +3            |
| **SHOULD** | Zoom float precision handling                  | +3             | +2            |
| **SHOULD** | Callbacks with data↔screen coordinate conver…  | +3             | +2            |
| **SHOULD** | Decimation out of scope — consumer's respons…  | +3             | +3            |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow…  | +3             | +3            |
| **SHOULD** | WebGL rejected                                 | +3             | +3            |
| **COULD**  | Bands: two-series API OR Dygraphs customBars…  | +1             | 0             |
| **COULD**  | Drawing order: bands → lines → points → high…  | +1             | +1            |
| **COULD**  | Highlight border defaults                      | +1             | +1            |
| **COULD**  | Time scales linear-only; best-effort at V0; …  | +1             | +1            |
| **COULD**  | Date inputs accepted alongside numeric times…  | +1             | 0             |
| **COULD**  | Empty data → fallback axis range; no built-i…  | +1             | +1            |
| **COULD**  | Live/append data = full redraws; no streamin…  | +1             | +1            |
| **COULD**  | Float32 sufficient post-normalization; norma…  | +1             | 0             |
| **COULD**  | OffscreenCanvas/Workers deferred               | +1             | +1            |
| **COULD**  | DOM for crosshair, zoom rectangle, and axes/…  | +1             | +1            |
| **COULD**  | Programmatic highlight with multiple independ… | +1             | +1            |
| **COULD**  | Virtualization for off-viewport charts         | +1             | +1            |
| **COULD**  | Canvas size handling: auto DPR + ResizeObser…  | +1             | +1            |
| **COULD**  | Robustness contract: type-correct config neve… | +1             | 0             |
| **COULD**  | Visual regression via headless canvas; noise…  | +1             | 0             |
| **COULD**  | Multiple Y-axes planned, not in initial cut    | +1             | 0             |
| **COULD**  | CSS variables preferred for styling; canvas-…  | +1             | 0             |

**Notes:**

- **condensed-500 S20 (Zoom float precision, +2):** "Drag-rect zoom, float-precision-safe" addresses
  the concern but omits the specific handling: fail-silently/nudge as minimum, reject with message
  and show clamped range as the ideal.
- **condensed-500 S21 (Callbacks, +2):** data↔screen converters are present but the specific
  callback types (hover, zoom, zoom-reset, event pass-through) are not listed.
- **condensed-500 C1 (Bands, 0):** Two API forms are present ("two series, or Dygraphs `customBars`
  triplets") but edges-drawn-independently is absent. No partial credit for Could.
- **condensed-500 C8 (Float32, 0):** Only "Data normalization, also the internal storage format"
  appears; Float32 sufficiency post-normalization is not mentioned.
- **condensed-500 C15 (Visual regression, 0):** Cairo preference and all noise-mitigation techniques
  are present, but pre-generated test data is not mentioned.
- **condensed-500 C5, C14, C16, C17 (0):** Date inputs, robustness contract, multiple Y-axes, and
  CSS variables theming are entirely absent.

### Summary

| Tier                   | condensed-1400 | condensed-500 |
| ---------------------- | -------------- | ------------- |
| Must (out of 8)        | 8+             | 8+            |
| Should (out of 16)     | 16+            | 14+ 2±        |
| Could (out of 17)      | 17+            | 9+            |
| Total points (145 max) | 145            | 135           |
| **Score**              | **100%**       | **93%**       |
