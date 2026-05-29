# CC-Base Spec Evaluation Report

Specs evaluated:

- `spec-1` → `cc-base/spec-1.md` (Velox Plot)
- `spec-2` → `cc-base/spec-2.md` (PlotLib)
- `spec-3` → `cc-base/spec-3.md` (Canvas Plot)

Criteria file: `reference-spec/tech-criteria.md`

---

## Structural Evaluation

### Topics

| Topic              | spec-1 | spec-2 | spec-3 |
| ------------------ | ------ | ------ | ------ |
| Goal               | 3      | 3      | 3      |
| Requirements       | 3      | 3      | 3      |
| Solution           | 4      | 4      | 4      |
| Out of scope       | 3      | 3      | 3      |
| Uncertainty        | 4      | 3      | 3      |
| **Total (max 17)** | **17** | **16** | **16** |

**Notes:**

- All three specs open with the title as top-level heading and have a dedicated Goals section, a
  dedicated Out of Scope section, and explicit alternative-rejection sections (WebGL,
  OffscreenCanvas) that earn full Solution credit.
- **Uncertainty — spec-1 (4):** §18 Open Questions includes a "Default assumption" column, making
  assumptions explicitly listed (+1). Also has a dedicated open-questions section (+1), risk
  discussion in §13.2 (+1), and open questions list (+1) = 4.
- **Uncertainty — spec-2 (3) and spec-3 (3):** Both have a dedicated open-questions section and some
  risk discussion, but no explicit assumptions list. spec-2 discusses the pixel-coord vs
  zoom-normalized trade-off as a risk in §7.4; spec-3 discusses silent symlog promotion and
  point-suppression thresholds.

### Metrics

| Metric               | spec-1 | spec-2 | spec-3 |
| -------------------- | ------ | ------ | ------ |
| Word count           | 2 395  | 2 872  | 2 639  |
| Avg section length   | 51.0   | 53.2   | 77.5   |
| Avg paragraph length | 27.3   | 28.4   | 34.2   |
| Avg bullet length    | 9.5    | 12.9   | 16.8   |
| Code snippets ratio  | 37%    | 30%    | 30%    |

---

## Technical Evaluation

### Criteria scores

| Tier       | Criterion                                      | spec-1 | spec-2 | spec-3 |
| ---------- | ---------------------------------------------- | ------ | ------ | ------ |
| **MUST**   | Canvas-based, performance-focused library for… | +10    | +10    | +10    |
| **MUST**   | Performance target ≥ uPlot, benchmarked with…  | 0      | +5     | +5     |
| **MUST**   | Independent X values per series                | +10    | +10    | +10    |
| **MUST**   | Log scale as a special case of symlog          | +10    | +10    | +5     |
| **MUST**   | Shared zoom+highlight reactive-only — does N…  | +10    | +10    | +10    |
| **MUST**   | Path2D cache stored in zoom-normalized data …  | +5     | −10    | +5     |
| **MUST**   | Stable series ids as cache keys                | +10    | +10    | +10    |
| **MUST**   | Data normalization to handle ranges where max… | 0      | 0      | 0      |
| **SHOULD** | Canonical use case: ML training metrics dash…  | +3     | +3     | +3     |
| **SHOULD** | Main benchmark: 100k points per chart          | +2     | +2     | +2     |
| **SHOULD** | Concrete FPS benchmark scenarios               | +2     | +2     | +2     |
| **SHOULD** | Symlog parametrization auto-derived from data… | +3     | +3     | +3     |
| **SHOULD** | Tick placement must match displayed label pre… | 0      | 0      | 0      |
| **SHOULD** | Auto-fit Y stays active under X-zoom; can onl… | +2     | +2     | +2     |
| **SHOULD** | Hover highlight: interpolated y at hovered x…  | +1     | +1     | +1     |
| **SHOULD** | NaN/missing values: skip and connect across    | +3     | +3     | +3     |
| **SHOULD** | Canvas stacking; highlighted marks drawn twic… | +2     | +2     | +2     |
| **SHOULD** | Framework-agnostic core with thin declarativ…  | +3     | +2     | +3     |
| **SHOULD** | Input formats: number[], Float32Array, Float…  | +2     | +2     | +2     |
| **SHOULD** | Zoom float precision handling                  | 0      | 0      | 0      |
| **SHOULD** | Callbacks with data↔screen coordinate conver…  | 0      | 0      | +1     |
| **SHOULD** | Decimation out of scope — consumer's respons…  | +3     | 0      | +2     |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow…  | +3     | +3     | +3     |
| **SHOULD** | WebGL rejected                                 | +3     | +3     | +3     |
| **COULD**  | Bands: two-series API OR Dygraphs customBars…  | 0      | 0      | 0      |
| **COULD**  | Drawing order: bands → lines → points → high…  | 0      | +1     | 0      |
| **COULD**  | Highlight border defaults                      | 0      | 0      | 0      |
| **COULD**  | Time scales linear-only; best-effort at V0; …  | 0      | 0      | 0      |
| **COULD**  | Date inputs accepted alongside numeric times…  | 0      | 0      | 0      |
| **COULD**  | Empty data → fallback axis range; no built-i…  | 0      | 0      | 0      |
| **COULD**  | Live/append data = full redraws; no streamin…  | 0      | 0      | +1     |
| **COULD**  | Float32 sufficient post-normalization; norma…  | 0      | 0      | 0      |
| **COULD**  | OffscreenCanvas/Workers deferred               | +1     | +1     | +1     |
| **COULD**  | DOM for crosshair, zoom rectangle, and axes/…  | +1     | +1     | +1     |
| **COULD**  | Programmatic highlight with multiple independ… | 0      | 0      | 0      |
| **COULD**  | Virtualization for off-viewport charts         | +1     | +1     | +1     |
| **COULD**  | Canvas size handling: auto DPR + ResizeObser…  | 0      | 0      | 0      |
| **COULD**  | Robustness contract: type-correct config neve… | 0      | 0      | 0      |
| **COULD**  | Visual regression via headless canvas; noise…  | 0      | 0      | 0      |
| **COULD**  | Multiple Y-axes planned, not in initial cut    | 0      | 0      | 0      |
| **COULD**  | CSS variables preferred for styling; canvas-…  | 0      | 0      | 0      |

### Notes on non-obvious scores

**MUST:**

- **M2 — spec-1 (0):** uPlot is not mentioned anywhere in spec-1; performance targets are expressed
  in ms without any comparison to uPlot.
- **M2 — spec-2, spec-3 (+5):** Both state ≥ uPlot performance ("match or exceed uPlot on
  throughput") but neither addresses that the comparison is against uPlot _without_ its decimation,
  or that uPlot's decimation misrepresents data.
- **M4 — spec-3 (+5):** spec-3's relationship is conditional — `scale: "log"` checks for
  non-positive data and promotes to symlog when found (with a `console.warn`). This is not the same
  as log being a strict special case of symlog that always uses the unified code path; non-positives
  are handled but not "uniformly."
- **M6 — spec-2 (−10):** spec-2 §7.4 explicitly states paths are built in **pixel (display)
  coordinates**, and argues against the zoom-normalized approach: _"This is simpler and faster than
  building in data-space and applying a CSS transform, which would require subpixel correction on
  every zoom level."_ This directly contradicts the criterion.
- **M6 — spec-1, spec-3 (+5):** Both use zoom-normalized coords with canvas transform ✓, but neither
  restricts invalidation to large/order-of-magnitude zoom changes. spec-1 re-derives symlog `C` on
  every zoom (causing frequent cache invalidation for symlog charts); spec-3 explicitly states "zoom
  level change → cache is invalidated per affected series."
- **M8 — all (0):** None of the three specs mention handling ranges where
  `max − min > Number.MAX_VALUE`.

**SHOULD:**

- **S2 — all (+2):** All state 100k as the main benchmark but none break it into the two
  configurations (100+ series × 1000 pts AND 1000+ series × 100 pts) that show it works for both
  layouts.
- **S3 — all (+2):** All provide concrete time-budget targets but express them in ms, not ≫60 / >30
  FPS tiers, and none give the multi-configuration scenario breakdown.
- **S5 — all (0):** None mention the constraint that tick placement must match displayed label
  precision exactly.
- **S6 — all (+2):** All imply Y auto-range under X-zoom (spec-2 and spec-3 say it explicitly;
  spec-1 implies it by prohibiting Y gesture zoom), but none state the "can only narrow last
  user-set Y range, never widen" rule.
- **S7 — all (+1):** All use nearest-point binary search for hover highlight. The reference spec
  requires interpolating Y at the hovered X position (not snapping to the nearest defined point);
  this interpolation is absent from all three.
- **S9 — all (+2):** All have a two-canvas stack (main + highlight), but: spec-1 does redraw a
  highlighted series on the overlay canvas ✓; spec-2 and spec-3 draw only a dot/marker on the
  highlight canvas, not the full series path. None explicitly state the design assumption that the
  highlighted set ≪ total.
- **S10 — spec-2 (+2):** spec-2's architecture is React-centric throughout; `PlotController` is a
  plain class but the chart rendering layer has no separate non-React entry point. Partial credit
  for framework-agnostic controller.
- **S11 — all (+2):** All accept `Float64Array` and `number[]` (the latter coerced); none mention
  `number[][]` row-oriented input.
- **S12 — all (0):** None mention zoom float-precision handling (fail-silently/nudge minimum,
  reject-with-message ideal, clamped range in zoom rectangle).
- **S13 — spec-3 (+1):** spec-3 has `onZoom` and `onHighlight` callbacks with a payload (series
  label, x, y), but no data↔screen coordinate conversions in payloads.
- **S14 — spec-2 (0):** Decimation is absent from spec-2's out-of-scope list and not addressed
  elsewhere.
- **S14 — spec-3 (+2):** §13 Open Questions notes "callers pre-aggregate server-side" and defers a
  decimation hook, addressing the concept but not as an explicit out-of-scope statement.

**COULD:**

- **C2 — spec-2 (+1):** §6.5 Rendering Order explicitly lists: bands → lines → points → ±Inf
  markers. Others do not state the draw order.
- **C7 — spec-3 (+1):** §13 Open Questions explicitly describes streaming as "re-running
  normalisation and invalidating the Path2D cache," making the full-redraw behavior clear. spec-1
  and spec-2 do not address this.
- **C13 — all (0):** All mention DPR cap and `ResizeObserver`, but none describe verifying canvas
  allocation or reducing raster size on allocation failure.
- **C14 — all (0):** spec-2 comes closest with a dedicated §15 Error Handling section, but
  production mode clamps rather than throwing for malformed inputs, so the "clearly malformed inputs
  throw with descriptive messages" contract is not fully met.

### Summary

| Tier                   | spec-1  | spec-2   | spec-3  |
| ---------------------- | ------- | -------- | ------- |
| Must (out of 8)        | 5+ 1±   | 5+ 1± 1− | 4+ 3±   |
| Should (out of 16)     | 7+ 6±   | 5+ 7±    | 6+ 8±   |
| Could (out of 17)      | 3+      | 4+       | 4+      |
| Total points (145 max) | 90      | 77       | 92      |
| **Score**              | **62%** | **53%**  | **63%** |
