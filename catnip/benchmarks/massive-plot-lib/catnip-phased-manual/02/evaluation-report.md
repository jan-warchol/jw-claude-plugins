# Catnip-Phased-Manual/02 Spec Evaluation Report

Specs evaluated:
- `initial` → `02/initial.md`
- `enriched` → `02/enriched.md`
- `c-1500` → `02/compressed-1500w.md`
- `c-1000` → `02/compressed-1000w.md`

Criteria file: `reference-spec/tech-criteria.md`

---

## Structural Evaluation

### Topics

| Topic | initial | enriched | c-1500 | c-1000 |
|-------|---------|----------|--------|--------|
| Goal | 3 | 3 | 3 | 3 |
| Requirements | 3 | 3 | 3 | 3 |
| Solution | 4 | 4 | 4 | 4 |
| Out of scope | 3 | 3 | 3 | 3 |
| Uncertainty | 0 | 4 | 4 | 4 |
| **Total (max 17)** | **13** | **17** | **17** | **17** |

**Notes:**

- All four earn full Goal (Overview clearly states purpose and performance targets), Requirements (Performance Constraints table), Solution (canvas architecture with canvas layering, Path2D caching, virtualization, and rejected backends), and Out of Scope marks.
- **Uncertainty — initial (0):** No risks, assumptions, or open questions.
- **Uncertainty — enriched, c-1500, c-1000 (4):** All contain "Assumptions, Risks, and Open Questions" with all three subsections. The enrichment step also adds a "Design Rationale" section giving explicit WHY reasoning for each major design decision (two canvases, zoom-normalized coords, DOM axes, reactive-only controller). c-1000 compresses the uncertainty content to a minimal paragraph but retains all three categories (+1 each) and the dedicated section (+1).

### Metrics

| Metric | initial | enriched | c-1500 | c-1000 |
|--------|---------|----------|--------|--------|
| Word count | 1 360 | 2 264 | 1 309 | 834 |
| Avg section length | 53.9 | 65.7 | 69.3 | 45.7 |
| Avg paragraph length | 30.2 | 38.3 | 30.1 | 21.0 |
| Avg bullet length | 11.5 | 16.4 | 13.1 | 9.9 |
| Code snippets ratio | 23% | 18% | 21% | 26% |

---

## Technical Evaluation

### Criteria scores

| Tier | Criterion | init | enr | c-1500 | c-1000 |
|------|-----------|------|-----|--------|--------|
| **MUST** | Canvas-based, performance-focused library for… | +10 | +10 | +10 | +10 |
| **MUST** | Performance target ≥ uPlot, benchmarked with… | +5 | +5 | +5 | +5 |
| **MUST** | Independent X values per series | +10 | +10 | +10 | +10 |
| **MUST** | Log scale as a special case of symlog | +10 | +10 | +10 | +10 |
| **MUST** | Shared zoom+highlight reactive-only — does N… | +10 | +10 | +10 | +10 |
| **MUST** | Path2D cache stored in zoom-normalized data … | +5 | +5 | +5 | +5 |
| **MUST** | Stable series ids as cache keys | +10 | +10 | +10 | +10 |
| **MUST** | Data normalization to handle ranges where max… | 0 | 0 | 0 | 0 |
| **SHOULD** | Canonical use case: ML training metrics dash… | +3 | +3 | +3 | +3 |
| **SHOULD** | Main benchmark: 100k points per chart | +3 | +3 | +3 | +2 |
| **SHOULD** | Concrete FPS benchmark scenarios | +2 | +2 | +2 | +2 |
| **SHOULD** | Symlog parametrization auto-derived from data… | +3 | +3 | +3 | +3 |
| **SHOULD** | Tick placement must match displayed label pre… | 0 | 0 | 0 | 0 |
| **SHOULD** | Auto-fit Y stays active under X-zoom; can onl… | 0 | +2 | +2 | +2 |
| **SHOULD** | Hover highlight: interpolated y at hovered x… | +1 | +1 | +1 | +1 |
| **SHOULD** | NaN/missing values: skip and connect across | +3 | +3 | +3 | +3 |
| **SHOULD** | Canvas stacking; highlighted marks drawn twic… | +2 | +2 | +2 | +2 |
| **SHOULD** | Framework-agnostic core with thin declarativ… | +1 | +1 | +1 | +1 |
| **SHOULD** | Input formats: number[], Float32Array, Float… | +2 | +2 | +2 | +2 |
| **SHOULD** | Zoom float precision handling | 0 | 0 | 0 | 0 |
| **SHOULD** | Callbacks with data↔screen coordinate conver… | +1 | +1 | +1 | +1 |
| **SHOULD** | Decimation out of scope — consumer's respons… | +3 | +3 | +3 | +3 |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow… | +3 | +3 | +3 | +3 |
| **SHOULD** | WebGL rejected | +3 | +3 | +3 | +3 |
| **COULD** | Bands: two-series API OR Dygraphs customBars… | 0 | 0 | 0 | 0 |
| **COULD** | Drawing order: bands → lines → points → high… | 0 | 0 | 0 | 0 |
| **COULD** | Highlight border defaults | 0 | 0 | 0 | 0 |
| **COULD** | Time scales linear-only; best-effort at V0; … | 0 | 0 | 0 | 0 |
| **COULD** | Date inputs accepted alongside numeric times… | 0 | 0 | 0 | 0 |
| **COULD** | Empty data → fallback axis range; no built-i… | 0 | 0 | 0 | 0 |
| **COULD** | Live/append data = full redraws; no streamin… | 0 | 0 | 0 | 0 |
| **COULD** | Float32 sufficient post-normalization; norma… | 0 | 0 | 0 | 0 |
| **COULD** | OffscreenCanvas/Workers deferred | +1 | +1 | +1 | +1 |
| **COULD** | DOM for crosshair, zoom rectangle, and axes/… | +1 | +1 | +1 | +1 |
| **COULD** | Programmatic highlight with multiple independ… | 0 | 0 | 0 | 0 |
| **COULD** | Virtualization for off-viewport charts | +1 | +1 | +1 | +1 |
| **COULD** | Canvas size handling: auto DPR + ResizeObser… | 0 | 0 | 0 | 0 |
| **COULD** | Robustness contract: type-correct config neve… | 0 | 0 | 0 | 0 |
| **COULD** | Visual regression via headless canvas; noise… | 0 | 0 | 0 | 0 |
| **COULD** | Multiple Y-axes planned, not in initial cut | 0 | 0 | 0 | 0 |
| **COULD** | CSS variables preferred for styling; canvas-… | 0 | 0 | 0 | 0 |

### Notes on non-obvious scores

**MUST:**

- **M6 (+5 for all):** All four specs use zoom-normalized [0,1]² coordinates for Path2D and apply a `DOMMatrix` transform at draw time ✓. Cache keys include `(series.id, zoomLevel)` where zoom level is quantized to 128 integer steps per decade — sub-level zooms reuse the cached path. However, 128 levels per decade means each level spans only 10^(1/128) ≈ 1.8% of a decade, so paths are rebuilt after every ~1.8% zoom change. The reference criterion's "invalidated only on large (order-of-magnitude) zoom changes" implies much coarser granularity (~10× zoom per rebuild). The core concept (zoom-normalized coords + canvas transform + level-based quantization) is present but the invalidation is significantly more frequent than the reference. Contrast with the 01 series, where paths are never invalidated on zoom at all.
- **M2 (+5 for all):** All state "match uPlot render throughput" and "PlotLib never decimates." None explicitly frame the comparison as being *without uPlot's decimation* or state that uPlot's decimation misrepresents data.
- **M8 (all 0):** Not mentioned.

**SHOULD:**

- **S2 — c-1000 (+2):** The Performance Constraints table in c-1000 just says "Max pts/chart | 100k" without listing the two explicit configurations (100 series × 1k pts, 1k series × 100 pts) present in the other three specs.
- **S6 — initial (0):** No Y-range or auto-fit behavior is described. Enrichment added the explicit statement "Zoom is X-only; Y auto-scales to the visible X range" (and the controller section "Y-axis is never synced; each chart auto-scales to visible Y independently"). The "narrow only, never widen" constraint is absent in all four.
- **S10 (+1 for all):** All specs are framed as "React-peered" libraries rather than "framework-agnostic core with thin React wrapper." The `Signal<T>` abstraction in the controller is framework-neutral, but no non-React entry point or explicit framework-agnostic claim is made.
- **S12 (all 0):** No float precision handling for extreme zoom is described. Initial and enriched mention a minimum drag of 4 CSS pixels and a minimum zoom-level quantization, but these are practical UX guards, not the float-precision failure handling the criterion describes.
- **S13 (+1 for all):** `onHover` callback is present with a detailed `HoverPoint` payload (seriesId, xIndex, x, y, isOutlier, isSpecial). No `onZoom` callback, no zoom-reset callback, no event pass-through, and no data↔screen coordinate conversions in payloads.
- **S14 (+3 for all):** "PlotLib never decimates" is stated throughout; Out of Scope explicitly lists "Client-side decimation: Callers aggregate server-side." Full credit — no client-side decimation of any kind, unlike the 03 series.
- **S15 (+3 for all):** "Zero runtime deps; React is a peer dependency" and "ESM only" are explicitly in the Performance Constraints table; SSR is in Out of Scope.

**COULD:**

- **C10 (+1 for all):** All four architecture diagrams/descriptions list crosshair as a `<div>` in the DOM overlay, zoom-rect as a `<div>`, and axes as `<span>` elements — all three are DOM, matching the criterion fully.
- **C11 (all 0):** The controller exposes `setHighlightX(x: number | null)` — a single scalar, not a set of independent marks. Unlike the 01 series which has `highlightedSeriesIds: Set<string>`.
- **C13 (all 0):** DPR cap and `ResizeObserver` are present ✓; the raster cap proactively reduces DPR when size would exceed the limit ✓. However, "verify allocation and reduce on failure" implies a reactive check after attempted allocation, which these specs do not describe.

### Summary

| Tier | initial | enriched | c-1500 | c-1000 |
|------|---------|----------|--------|--------|
| Must (out of 8) | 5+ 2± | 5+ 2± | 5+ 2± | 5+ 2± |
| Should (out of 16) | 7+ 6± | 7+ 7± | 7+ 7± | 6+ 8± |
| Could (out of 17) | 3+ | 3+ | 3+ | 3+ |
| Total points (145 max) | 93 | 95 | 95 | 94 |
| **Score** | **64%** | **66%** | **66%** | **65%** |
