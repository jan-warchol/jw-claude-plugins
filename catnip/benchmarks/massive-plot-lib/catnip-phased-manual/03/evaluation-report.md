# Catnip-Phased-Manual/03 Spec Evaluation Report

Specs evaluated:
- `initial` → `03/initial.md`
- `enriched` → `03/enriched.md`
- `c-1500` → `03/compressed-1500w.md`
- `c-1000` → `03/compressed-1000w.md`

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
| Uncertainty | 0 | 4 | 4 | 3 |
| **Total (max 17)** | **13** | **17** | **17** | **16** |

**Notes:**

- All four specs earn full Goal (Overview clearly states purpose), Requirements (Performance Targets table with specific ms targets), Solution (architecture clearly articulated with WebGL/OffscreenCanvas rejection rationale, explicit trade-offs), and Out of Scope marks.
- **Uncertainty — initial (0):** No risks, assumptions, or open questions anywhere in the document.
- **Uncertainty — enriched (4):** Dedicated "Risks, Assumptions, and Open Questions" section with all three subsections explicitly populated. +1 each for risks, assumptions, open questions, and dedicated section.
- **Uncertainty — c-1500 (4):** Same section structure as enriched, retained in full.
- **Uncertainty — c-1000 (3):** "Risks and Assumptions" section present; risks and assumptions are listed (+1 each), and the section is dedicated (+1). Open questions were dropped in compression (0).

### Metrics

| Metric | initial | enriched | c-1500 | c-1000 |
|--------|---------|----------|--------|--------|
| Word count | 1 769 | 2 664 | 1 307 | 844 |
| Avg section length | 67.8 | 83.1 | 51.5 | 62.5 |
| Avg paragraph length | 29.6 | 36.3 | 29.9 | 27.0 |
| Avg bullet length | 9.9 | 14.2 | 13.8 | 15.3 |
| Code snippets ratio | 19% | 17% | 26% | 33% |

---

## Technical Evaluation

### Criteria scores

| Tier | Criterion | init | enr | c-1500 | c-1000 |
|------|-----------|------|-----|--------|--------|
| **MUST** | Canvas-based, performance-focused library for… | +10 | +10 | +10 | +10 |
| **MUST** | Performance target ≥ uPlot, benchmarked with… | +5 | +5 | 0 | 0 |
| **MUST** | Independent X values per series | +10 | +10 | +10 | +10 |
| **MUST** | Log scale as a special case of symlog | +10 | +10 | +10 | +10 |
| **MUST** | Shared zoom+highlight reactive-only — does N… | +10 | +10 | +10 | +10 |
| **MUST** | Path2D cache stored in zoom-normalized data … | +5 | +5 | +5 | +5 |
| **MUST** | Stable series ids as cache keys | +10 | +10 | +10 | +10 |
| **MUST** | Data normalization to handle ranges where max… | 0 | 0 | 0 | 0 |
| **SHOULD** | Canonical use case: ML training metrics dash… | +3 | +3 | +3 | +3 |
| **SHOULD** | Main benchmark: 100k points per chart | +3 | +3 | +3 | +3 |
| **SHOULD** | Concrete FPS benchmark scenarios | +2 | +2 | +2 | +2 |
| **SHOULD** | Symlog parametrization auto-derived from data… | +3 | +3 | +3 | +3 |
| **SHOULD** | Tick placement must match displayed label pre… | 0 | 0 | 0 | 0 |
| **SHOULD** | Auto-fit Y stays active under X-zoom; can onl… | 0 | +2 | +2 | +2 |
| **SHOULD** | Hover highlight: interpolated y at hovered x… | +1 | +1 | +1 | +1 |
| **SHOULD** | NaN/missing values: skip and connect across | +3 | +3 | +3 | +3 |
| **SHOULD** | Canvas stacking; highlighted marks drawn twic… | +2 | +2 | +2 | +2 |
| **SHOULD** | Framework-agnostic core with thin declarativ… | +2 | +2 | +2 | +2 |
| **SHOULD** | Input formats: number[], Float32Array, Float… | +2 | +2 | +2 | +2 |
| **SHOULD** | Zoom float precision handling | 0 | 0 | 0 | 0 |
| **SHOULD** | Callbacks with data↔screen coordinate conver… | +2 | +2 | +2 | +2 |
| **SHOULD** | Decimation out of scope — consumer's respons… | +2 | +2 | +2 | +2 |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow… | +3 | +3 | +3 | +3 |
| **SHOULD** | WebGL rejected | +3 | +3 | +3 | +3 |
| **COULD** | Bands: two-series API OR Dygraphs customBars… | 0 | 0 | 0 | 0 |
| **COULD** | Drawing order: bands → lines → points → high… | 0 | 0 | 0 | 0 |
| **COULD** | Highlight border defaults | 0 | 0 | 0 | 0 |
| **COULD** | Time scales linear-only; best-effort at V0; … | 0 | 0 | 0 | 0 |
| **COULD** | Date inputs accepted alongside numeric times… | 0 | 0 | 0 | 0 |
| **COULD** | Empty data → fallback axis range; no built-i… | 0 | 0 | 0 | 0 |
| **COULD** | Live/append data = full redraws; no streamin… | 0 | +1 | +1 | +1 |
| **COULD** | Float32 sufficient post-normalization; norma… | 0 | 0 | 0 | 0 |
| **COULD** | OffscreenCanvas/Workers deferred | +1 | +1 | +1 | +1 |
| **COULD** | DOM for crosshair, zoom rectangle, and axes/… | 0 | 0 | 0 | 0 |
| **COULD** | Programmatic highlight with multiple independ… | 0 | 0 | 0 | 0 |
| **COULD** | Virtualization for off-viewport charts | +1 | +1 | +1 | +1 |
| **COULD** | Canvas size handling: auto DPR + ResizeObser… | 0 | 0 | 0 | 0 |
| **COULD** | Robustness contract: type-correct config neve… | 0 | 0 | 0 | 0 |
| **COULD** | Visual regression via headless canvas; noise… | 0 | 0 | 0 | 0 |
| **COULD** | Multiple Y-axes planned, not in initial cut | 0 | 0 | 0 | 0 |
| **COULD** | CSS variables preferred for styling; canvas-… | 0 | 0 | 0 | 0 |

### Notes on non-obvious scores

**MUST:**

- **M2 — initial, enriched (+5):** Both state "match uPlot on throughput" in the Overview, but neither addresses the key framing: that the comparison is fair *without* uPlot's decimation, and that decimation misrepresents data. The compressed versions drop the uPlot comparison entirely.
- **M2 — c-1500, c-1000 (0):** The Overview was rewritten to remove the uPlot comparison ("Zero-dependency, ESM-only, React-peer charting library for ML training dashboards" — no uPlot mention).
- **M6 — all (+5):** All four specs use zoom-normalized [0,1]² coordinates with `ctx.setTransform()` at draw time ✓, but cache keys include `(xMin, xMax, yMin, yMax, ...)` — every zoom viewport change produces a cache miss, not only large/order-of-magnitude changes. This is a different invalidation policy than the reference.
- **M8 — all (0):** Not mentioned in any spec. The normalization passes described deal with NaN/Inf, not precision loss from `max − min > Number.MAX_VALUE`.

**SHOULD:**

- **S2 — all (+3):** Unlike the cc-base specs, all four here explicitly include *both* configurations in the Performance Targets table (100 series × 1 000 pts AND 1 000 series × 100 pts), earning full credit.
- **S3 — all (+2):** Performance targets are expressed in ms (≤16 ms, ≤4 ms), not ≫60 / >30 FPS tiers with named small/large scenarios.
- **S6 — initial (0):** The initial spec has no Y range or auto-fit section at all; this was added during the enrichment step. Enriched and both compressions earn +2 for "auto-fits to min/max of visible data in xRange" (but the "narrow only, never widen" constraint is absent in all).
- **S7 — all (+1):** All use binary search for the nearest defined point per series. The reference requires interpolating Y at the hovered X (not constrained to defined points), which none of these specs implement.
- **S9 — all (+2):** Stacked canvases ✓. However, the highlight canvas holds the crosshair and hovered point markers — not the full series redrawn at emphasis. The reference spec's "drawn twice" means the highlighted series is drawn normally on the main canvas *and* redrawn with highlight on the overlay; that is not what these specs describe. The "highlighted set ≪ total" assumption is not stated.
- **S10 — all (+2):** The `SharedController` interface has "a framework-agnostic subscribe/notify interface" ✓, but the `<Chart>` component is React-only with no separate non-React entry point mentioned.
- **S11 — all (+2):** Series accepts `Float64Array` only; enriched explicitly states "Callers using plain `number[]` must convert; the library does not accept plain arrays." `Float32Array` and `number[][]` are absent.
- **S13 — all (+2):** `onZoom` and `onHover` callbacks are present; `HoveredPoint` carries data-coord x/y. Zoom-reset and event pass-through callbacks are absent, and no data↔screen coordinate conversions appear in payloads.
- **S14 — all (+2):** Server-side decimation is the caller's responsibility ✓. However, all four specs specify that the library *does* perform a client-side min/max decimation pass when points exceed pixel width — making decimation partially in-scope. The reference spec treats decimation as entirely out of scope.

**COULD:**

- **C7 — initial (0), enriched/c-1500/c-1000 (+1):** Enriched added an explicit "Data Updates" section: "The library does not expose an append API. To update a series... replace the series object." This was retained in both compressions. Initial lacks any live-data discussion.
- **C10 — all (0):** Zoom rectangle and axes/labels are DOM ✓, but the crosshair is drawn on the highlight *canvas* (not DOM). The criterion requires DOM for crosshair too; not fully satisfied.
- **C13 — all (0):** DPR cap and `ResizeObserver` are present ✓; raster cap is described as a proactive ceiling ✓. However, none describe verifying allocation success or reducing size after an allocation failure.
- **C14 — all (0):** Enriched, c-1500, and c-1000 explicitly state that monotonicity violations are "undefined behavior; no runtime check is performed," which is inconsistent with "clearly malformed inputs throw with descriptive messages."

### Summary

| Tier | initial | enriched | c-1500 | c-1000 |
|------|---------|----------|--------|--------|
| Must (out of 8) | 5+ 2± | 5+ 2± | 5+ 1± | 5+ 1± |
| Should (out of 16) | 6+ 7± | 6+ 8± | 6+ 8± | 6+ 8± |
| Could (out of 17) | 2+ | 3+ | 3+ | 3+ |
| Total points (145 max) | 93 | 96 | 91 | 91 |
| **Score** | **64%** | **66%** | **63%** | **63%** |
