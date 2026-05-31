# Structural Evaluation — massive-plot-lib catnip-phased-tasks

**File mapping:**
- `01` → `01/compressed.md`
- `02` → `02/compressed.md`
- `03` → `03/compressed.md`

## Topics comparison

| Topic | 01 | 02 | 03 |
|---|---|---|---|
| Goal | 3 | 3 | 3 |
| Requirements | 3 | 3 | 3 |
| Solution | 4 | 4 | 4 |
| Out of scope | 3 | 3 | 3 |
| Uncertainty | 4 | 4 | 4 |
| **Total (max 17)** | **17** | **17** | **17** |

All three specs achieve a perfect structural score — each has dedicated sections for every topic, verifiable requirements, explicit design rationale with alternatives rejected, and an uncertainty section covering risks, assumptions, and open questions.

## Metrics comparison

| Metric | 01 | 02 | 03 |
|---|---|---|---|
| Word count | 1130 | 1112 | 1101 |
| Avg section length | 71.7 | 62.1 | 54.8 |
| Avg paragraph length | 55.2 | 38.7 | 42.5 |
| Avg bullet length | 13.6 | 13.1 | 12.9 |
| Code snippets ratio | 22% | 19% | 18% |

The three specs are nearly identical in word count (~1100–1130 words). The main structural difference is that **01** packs its content into fewer, longer sections (avg 71.7 words vs 54.8 for 03), while **03** distributes content across more granular sections — its lower avg paragraph length (42.5) alongside a lower avg section length points to more frequent heading breaks rather than shorter prose. **02** sits between the two on most metrics.

## Technical evaluation

Criteria source: `catnip/benchmarks/massive-plot-lib/tech-criteria.md`

| Tier | Criterion | 01 | 02 | 03 |
|------|-----------|----|----|-----|
| **MUST** | Canvas-based, performance-focused library fo… | +10 | +10 | +10 |
| **MUST** | Performance target ≥ uPlot, benchmarked with… | +5 | 0 | +10 |
| **MUST** | Independent X values per series | +10 | +10 | +10 |
| **MUST** | Log scale as a special case of symlog | −10 | −10 | +5 |
| **MUST** | Shared zoom+highlight reactive-only — does N… | +10 | +10 | +10 |
| **MUST** | Path2D cache stored in zoom-normalized data … | +5 | +5 | +10 |
| **MUST** | Stable series ids as cache keys | +10 | +10 | +10 |
| **MUST** | Data normalization to handle ranges where ma… | 0 | 0 | 0 |
| **SHOULD** | Canonical use case: ML training metrics dash… | +3 | +2 | +3 |
| **SHOULD** | Main benchmark: 100k points per chart | +3 | 0 | +2 |
| **SHOULD** | Concrete FPS benchmark scenarios | 0 | 0 | 0 |
| **SHOULD** | Symlog parametrization auto-derived from dat… | −3 | +3 | +3 |
| **SHOULD** | Tick placement must match displayed label pr… | 0 | 0 | 0 |
| **SHOULD** | Auto-fit Y stays active under X-zoom; can o… | 0 | 0 | 0 |
| **SHOULD** | Hover highlight: interpolated y at hovered x… | 0 | 0 | 0 |
| **SHOULD** | NaN/missing values: skip and connect across | +3 | +3 | +3 |
| **SHOULD** | Canvas stacking; highlighted marks drawn twi… | +2 | +2 | +2 |
| **SHOULD** | Framework-agnostic core with thin declarati… | 0 | 0 | 0 |
| **SHOULD** | Input formats: number[], Float32Array, Float… | −3 | 0 | 0 |
| **SHOULD** | Zoom float precision handling | 0 | 0 | 0 |
| **SHOULD** | Callbacks with data↔screen coordinate conve… | 0 | +1 | 0 |
| **SHOULD** | Decimation out of scope — consumer's respon… | +3 | +3 | +3 |
| **SHOULD** | Zero deps, ESM-only, React as peer dep, brow… | +3 | +3 | +3 |
| **SHOULD** | WebGL rejected | +3 | +3 | +3 |
| **COULD** | OffscreenCanvas/Workers deferred | +1 | +1 | +1 |
| **COULD** | DOM for crosshair, zoom rectangle, and axes… | +1 | +1 | +1 |
| **COULD** | Virtualization for off-viewport charts | +1 | +1 | +1 |
| **COULD** | (all other 14 could criteria) | 0 | 0 | 0 |

### Notes on non-obvious scores

- **Log as special case of symlog:** All three specs treat log as a separate code path with throws/warnings on non-positive values, directly contradicting the criterion. Spec-03 Requirements says "log is symlog with threshold → 0" but its Solution section explicitly contradicts this ("log is a separate code path, not a degenerate symlog"), so partial credit.
- **Performance target ≥ uPlot:** Spec-01 says "uPlot-level render throughput" but never frames it as a benchmark or addresses the decimation distortion point — partial. Spec-02 gives a 5 ms draw-time target without mentioning uPlot at all.
- **Path2D zoom-normalized coords:** All three describe normalized [0,1] paths with `ctx.setTransform`. The "invalidated only on large zoom changes" nuance (float precision at extreme zoom) is unaddressed; spec-03 says "zoom/pan never invalidates," which satisfies the spirit and earns full credit.
- **Symlog manual override:** Spec-01 says "no manual tuning," directly contradicting the requirement for an override prop — negative score.
- **Input formats:** Spec-01 explicitly says "Float64Array required (not number[])" — a direct contradiction. Specs 02 and 03 simply don't mention number[] or number[][] row-oriented formats.
- **Canvas stacking partial:** All three describe a layered canvas stack but none mentions "highlighted marks drawn twice" or that the design assumes a small highlighted set.

### Summary

| Tier | 01 | 02 | 03 |
|------|----|----|----|
| Must (out of 8) | 4+ 2± 1− | 4+ 1± 1− | 6+ 1± |
| Should (out of 16) | 6+ 1± 2− | 5+ 3± | 6+ 2± |
| Could (out of 17) | 3+ | 3+ | 3+ |
| Total points (145 max) | 57 | 58 | 90 |
| **Score** | **39%** | **40%** | **62%** |
