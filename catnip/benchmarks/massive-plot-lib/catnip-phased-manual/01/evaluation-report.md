# Catnip-Phased-Manual/01 Spec Evaluation Report

Specs evaluated:
- `initial` → `01/initial.md`
- `enriched` → `01/enriched.md`
- `c-1500` → `01/compressed-1500w.md`
- `c-1000` → `01/compressed-1000w.md`

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

- All four specs earn the same Goal (clear Purpose section), Requirements (Scale Targets table + Performance Constraints), Solution (architecture with canvas layering, Path2D caching, rejected backends), and Out of Scope marks.
- **Uncertainty — initial (0):** No risks, assumptions, or open questions anywhere.
- **Uncertainty — enriched, c-1500, c-1000 (4):** All three contain a dedicated "Risks, Assumptions, and Open Questions" section with all three subsections. Notably, c-1000 at only 718 words retains the full uncertainty structure, just compressed into prose (bullets → inline text). +1 each for risks, assumptions, open questions, and dedicated section.

### Metrics

| Metric | initial | enriched | c-1500 | c-1000 |
|--------|---------|----------|--------|--------|
| Word count | 1 513 | 2 537 | 1 279 | 718 |
| Avg section length | 60.0 | 78.8 | 58.0 | 48.6 |
| Avg paragraph length | 36.5 | 45.8 | 30.3 | 24.7 |
| Avg bullet length | 17.4 | 21.0 | 11.2 | 9.6 |
| Code snippets ratio | 20% | 21% | 30% | 32% |

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
| **MUST** | Path2D cache stored in zoom-normalized data … | +10 | +10 | +10 | +10 |
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
| **SHOULD** | Framework-agnostic core with thin declarativ… | +1 | +1 | +1 | +1 |
| **SHOULD** | Input formats: number[], Float32Array, Float… | +2 | +2 | +2 | +2 |
| **SHOULD** | Zoom float precision handling | 0 | +2 | +2 | +2 |
| **SHOULD** | Callbacks with data↔screen coordinate conver… | +1 | +1 | +1 | +1 |
| **SHOULD** | Decimation out of scope — consumer's respons… | +3 | +3 | +3 | +3 |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow… | +2 | +2 | +2 | +2 |
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
| **COULD** | Programmatic highlight with multiple independ… | +1 | +1 | +1 | +1 |
| **COULD** | Virtualization for off-viewport charts | +1 | +1 | +1 | +1 |
| **COULD** | Canvas size handling: auto DPR + ResizeObser… | 0 | 0 | 0 | 0 |
| **COULD** | Robustness contract: type-correct config neve… | 0 | 0 | 0 | 0 |
| **COULD** | Visual regression via headless canvas; noise… | 0 | 0 | 0 | 0 |
| **COULD** | Multiple Y-axes planned, not in initial cut | 0 | 0 | 0 | 0 |
| **COULD** | CSS variables preferred for styling; canvas-… | 0 | 0 | 0 | 0 |

### Notes on non-obvious scores

**MUST:**

- **M6 (+10 for all):** This is the key differentiator from other spec sets. All four specs use the **series ID alone** as the cache key — not viewport coords. Paths are built in zoom-normalized [0,1]² coordinates (relative to the series' full data extent) and a `DOMMatrix` affine transform is applied at draw time. The consequence is that *pan and zoom never invalidate the path cache at all* — only data changes or series add/remove do. This fully satisfies the criterion and exceeds its "only on large zoom changes" requirement.
- **M2 (+5 for all):** All four retain the uPlot comparison ("match uPlot's raw render throughput," "throughput ≥ uPlot") and affirm no client-side decimation. However, none state that uPlot's decimation *misrepresents data* or that the comparison is specifically benchmarked without uPlot's decimation pass.
- **M8 (all 0):** Not mentioned in any spec.

**SHOULD:**

- **S2 (+3 for all):** Scale Targets table explicitly lists both configurations (100 series × 1 000 pts AND 1 000 series × 100 pts) in the Notes column, earning full credit — unlike many other spec sets.
- **S6 — initial (0):** The initial spec has no Y-domain or auto-fit section. Enrichment added the Y-Domain Behavior section (Y auto-fits to visible xWindow); this was retained in both compressions. None state the "narrow only, never widen" constraint — partial credit (+2) for the three enriched/compressed specs.
- **S10 (+1 for all):** All four describe the library as "an ESM-only React library" throughout. The `ChartController.subscribe()` interface has framework-agnostic potential, but no explicit non-React entry point or "framework-agnostic core" claim is made. Scores lower than the 03 series (which explicitly called out a framework-agnostic subscribe/notify interface).
- **S12 — initial (0), enriched/c-1500/c-1000 (+2):** The enrichment step added zoom limits ("minimum zoom: the window must span at least 2 distinct x values") and a Risks section discussing float32 precision loss at extreme zoom with the normalization scheme as mitigation. This is a "fail silently via minimum limit" approach — partial credit for addressing the concept, though not the "show clamped range in zoom rectangle" ideal.
- **S13 (+1 for all):** `onSeriesHover` callback is present (and `onPointClick` in enriched and compressions). No `onZoom` callback, no zoom-reset callback, no event pass-through, no data↔screen coordinate conversions in payloads.
- **S14 (+3 for all):** Unlike the 03 series (which performed client-side min/max decimation when points exceeded pixel width), these specs explicitly state "No client-side decimation" and "Client never decimates" — earning full credit.
- **S15 (+2 for all):** Zero-dependency, ESM-only, and no-SSR are clearly stated. React is described as the library's own framework ("an ESM-only React library"), not explicitly as a peer dependency. The Environment Requirements section (enriched) states "React ≥ 18.0" without specifying peer dep status.

**COULD:**

- **C10 (+1 for all):** All four architecture descriptions list "crosshair" explicitly in the DOM overlay layer (alongside axes and tooltip anchor). This contrasts with the 03 series, where crosshair was on the highlight canvas. Note: the Interaction sections in some specs contradict this by mentioning "highlight canvas" for crosshair — the Architecture section is treated as authoritative.
- **C11 (+1 for all):** `ChartController.highlightedSeriesIds: Set<string>` allows multiple series highlighted simultaneously via a programmatic interface. This directly satisfies "programmatic highlight with multiple independent marks" — a feature absent in the 03 series where highlight was a single `highlightX` number.
- **C13 (all 0):** DPR cap and `ResizeObserver` are present ✓; the raster cap (`MAX_CANVAS_PIXELS`) is described as a proactive ceiling ✓. Verifying allocation and reducing size on failure are not described.
- **C17 (all 0):** Out of Scope explicitly includes "no CSS custom property theming," which contradicts the criterion.

### Summary

| Tier | initial | enriched | c-1500 | c-1000 |
|------|---------|----------|--------|--------|
| Must (out of 8) | 6+ 1± | 6+ 1± | 6+ 1± | 6+ 1± |
| Should (out of 16) | 5+ 7± | 5+ 9± | 5+ 9± | 5+ 9± |
| Could (out of 17) | 4+ | 4+ | 4+ | 4+ |
| Total points (145 max) | 98 | 102 | 102 | 102 |
| **Score** | **68%** | **70%** | **70%** | **70%** |
