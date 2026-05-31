# Technical Evaluation — massive-plot-lib phased tasks

Spec fidelity scored against `catnip/benchmarks/massive-plot-lib/tech-criteria.md`.

## File mapping

| Col | Path (relative to project dir) |
| --- | --- |
| **A** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/01/initial.md` |
| **B** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/01/enriched.md` |
| **E** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/01/compressed.md` |
| **C** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/02/initial.md` |
| **D** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/02/enriched.md` |
| **F** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/02/compressed.md` |
| **G** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/03/initial.md` |
| **H** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/03/enriched.md` |
| **I** | `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks/03/compressed.md` |

Phase order per lineage: initial → enriched → compressed (01: A → B → E; 02: C → D → F; 03: G → H → I).

## Full scoring table

| Tier | Criterion | A | B | E | C | D | F | G | H | I |
| ---- | --------- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| **MUST** | Canvas-based, performance-focused library fo… | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Performance target ≥ uPlot, benchmarked with… | +10 | +10 | +10 | +10 | +10 | +5 | +10 | +10 | +10 |
| **MUST** | Independent X values per series | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Log scale as a special case of symlog | +10 | +5 | +5 | +5 | +5 | 0 | +10 | +10 | +10 |
| **MUST** | Shared zoom+highlight reactive-only — does N… | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Path2D cache stored in zoom-normalized data … | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Stable series ids as cache keys | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Data normalization to handle ranges where ma… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **SHOULD** | Canonical use case: ML training metrics dash… | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Main benchmark: 100k points per chart | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Concrete FPS benchmark scenarios | +2 | +3 | +3 | +1 | +2 | +2 | +2 | +2 | +2 |
| **SHOULD** | Symlog parametrization auto-derived from dat… | +2 | +2 | +2 | +2 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Tick placement must match displayed label pr… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **SHOULD** | Numeric axis labels robust for any range: ≥2… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **SHOULD** | Auto-fit Y stays active under X-zoom; can on… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **SHOULD** | Hover highlight: interpolated y at hovered x… | 0 | +1 | +1 | 0 | +1 | +1 | +1 | +1 | +1 |
| **SHOULD** | NaN/missing values: skip and connect across … | -3 | -3 | -3 | -3 | -3 | -3 | -3 | -3 | -3 |
| **SHOULD** | Non-finite value markers: NaN/±Inf represent… | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Integrated/built-in tooltip showing hovered … | 0 | 0 | 0 | 0 | 0 | 0 | +2 | +2 | +2 |
| **SHOULD** | Canvas stacking; highlighted marks drawn twi… | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Framework-agnostic core with thin declarativ… | +2 | +2 | +2 | +1 | +1 | +1 | +2 | +2 | +2 |
| **SHOULD** | Input formats: number[], Float32Array, Float… | 0 | +1 | +1 | +2 | +2 | +2 | +2 | +2 | +2 |
| **SHOULD** | Zoom float precision handling | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **SHOULD** | Callbacks with data↔screen coordinate conver… | +1 | +1 | +1 | +2 | +2 | +2 | +1 | +2 | +2 |
| **SHOULD** | Decimation out of scope — consumer's respons… | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow… | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | WebGL rejected | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 | +3 |
| **COULD** | Bands: two-series API OR Dygraphs customBars… | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Drawing order: bands → lines → points → high… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Highlight border defaults: bg color for line… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Time scales linear-only; best-effort at V0; … | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Date inputs accepted alongside numeric times… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Empty data → fallback axis range; no built-i… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Live/append data = full redraws; no streamin… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Float32 sufficient post-normalization; norma… | 0 | 0 | 0 | +1 | +1 | +1 | 0 | 0 | 0 |
| **COULD** | OffscreenCanvas/Workers deferred | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 |
| **COULD** | DOM for crosshair, zoom rectangle, and axes/… | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Programmatic highlight with multiple indepen… | +1 | +1 | +1 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Virtualization for off-viewport charts | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Canvas size handling: auto DPR + ResizeObser… | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Robustness contract: type-correct config nev… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Visual regression via headless canvas; noise… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Multiple Y-axes planned, not in initial cut | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | CSS variables preferred for styling; canvas-… | 0 | 0 | 0 | -1 | -1 | 0 | -1 | -1 | 0 |
| **COULD** | Single-value ranges auto-expanded to include… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Configurable line stroke width, color, and d… | 0 | +1 | +1 | 0 | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Modern evergreen browsers only, last ~2 vers… | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **SHOULD NOT** | Automatic statistical outlier detection — re… | -3 | -3 | -3 | 0 | 0 | 0 | -3 | -3 | -3 |
| **SHOULD NOT** | Bundle-size target/budget | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Notes on non-obvious scores

- **Log as special case of symlog (MUST):** The decisive differentiator across lineages.
  - **03 (G/H/I): full 10** — states it in the criterion's exact direction ("log is a special case of symlog… when the linear width parameter → 0"), and symlog's `sign(x)·log(1+|x|/C)` handles non-positive values uniformly.
  - **A: full 10** — "treat pure log as a degenerate symlog."
  - **B/E, C/D: half 5** — B/E concede the relationship but implement log as a separate code path; C/D invert it ("symlog is treated as a special case of *log*"). All keep the conceptual link.
  - **F: 0** — compression dropped the relationship statement entirely.
- **Performance target ≥ uPlot (MUST):** All name uPlot as the bar and pair it with "no client-side decimation" (capturing the fairness nuance) — except **F**, where compression removed all uPlot/Dygraphs naming, leaving only an absolute target → half (5).
- **Normalization for max−min > Number.MAX_VALUE (MUST):** No spec addresses the extreme-dynamic-range overflow concept; normalization elsewhere is for NaN/sort/extent. 0 across the board.
- **NaN skip & connect across (SHOULD):** The reference wants line *continuity* across NaN; every spec does the opposite (pen-lift / gap) → contradiction, −3 for all.
- **Built-in tooltip (SHOULD):** Only the **03 lineage (G/H/I)** earns credit — a "tooltip anchor" in the DOM layer plus a "nearest-point value readout… in scope" → partial 2 (single-series, somewhat hedged). The 01/02 lineages provide a crosshair but no value readout → 0.
- **Automatic statistical outlier detection (SHOULD NOT):** Present in the **01 and 03 lineages** (σ- or IQR-based detection, `outlierFence`/`outlierThreshold`, `onOutliersFound`) → −3. The **02 lineage** implements only non-finite markers, no computed outliers → 0.
- **Symlog override (SHOULD):** A/B/E/C auto-derive with no override (partial); **D/F and all of 03** expose an explicit override (`symlogThreshold` / `threshold?`) → full.
- **CSS variables (COULD):** C/D and G/H explicitly place CSS custom properties / CSS-variable theming out of scope → contradiction, −1. Their compressed forms (**F, I**) dropped the explicit CSS-variable mention, removing the contradiction → 0. The 01 lineage omits the topic → 0.
- **Programmatic multi-highlight (COULD):** 01 lineage exposes `selectedSeries: Set<string>` → +1; 02 and 03 use a single highlight target → 0.
- **Configurable stroke/width/dash (COULD):** Only **B/E** expose `lineWidth`/`dash`/`color` per-series props → +1. The 02 and 03 lineages expose color (and band styling) but not line width/dash as API props → 0.

## Summary

| Tier | A | B | E | C | D | F | G | H | I |
| ---- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Must (out of 8) | 7+ | 6+ 1± | 6+ 1± | 6+ 1± | 6+ 1± | 5+ 1± | 7+ | 7+ | 7+ |
| Should (out of 19) | 7+ 4± 1- | 8+ 5± 1- | 8+ 5± 1- | 7+ 5± 1- | 8+ 5± 1- | 8+ 5± 1- | 8+ 6± 1- | 8+ 6± 1- | 8+ 6± 1- |
| Could (out of 20) | 6+ | 7+ | 7+ | 6+ 1- | 6+ 1- | 6+ | 5+ 1- | 5+ 1- | 5+ |
| Should not (out of 2) | 1- | 1- | 1- | — | — | — | 1- | 1- | 1- |
| Total points (157 max) | 98 | 97 | 97 | 96 | 99 | 90 | 102 | 103 | 104 |
| **Score** | **62%** | **62%** | **62%** | **61%** | **63%** | **57%** | **65%** | **66%** | **66%** |

## Phase progression

| Spec | initial | enriched | compressed |
| ---- | ------- | -------- | ---------- |
| **01** | 98 (62%) | 97 (62%) | 97 (62%) |
| **02** | 96 (61%) | 99 (63%) | 90 (57%) |
| **03** | 102 (65%) | 103 (66%) | 104 (66%) |

- **01** is stable across all three phases.
- **02** peaked at enrich (99) but lost 9 points in compression (90), mainly from dropping the uPlot benchmark reference (MUST 10 → 5) and the log/symlog relationship (MUST 5 → 0), partly offset by losing the CSS-variable contradiction (COULD −1 → 0).
- **03** is the strongest lineage and the only one that gains slightly through every phase. Its lead comes from getting log-as-special-case-of-symlog right (full 10 throughout), a built-in tooltip, and an explicit symlog override — even while carrying the same outlier-detection (SHOULD NOT) penalty as the 01 lineage. Compression nudged it up by shedding the CSS-variable contradiction.
