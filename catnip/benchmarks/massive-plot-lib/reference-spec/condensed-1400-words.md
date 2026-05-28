# Plot library spec

Fast, canvas-based plotting library for massive data. Performance-focused; not a generic charting tool — concerns like decimation and initial axis sync are pushed to the consumer. Inspired by Dygraphs and uPlot, aiming to surpass them on selected axes.

## Canonical use case

ML training metrics dashboards: many charts, each with many series. Source data 1M+ points per series, server-aggregated to ≤100k points per chart. Drives these requirements:

- Spotting outliers across a pack of similar series — the reason 1M-point charts are useful at all.
- Markers for non-finite values (NaN/±Inf) drawn on top of the regular line, as bug indicators.
- Zooming in to see actual values once aggregation has hidden them.
- Synchronized zoom and highlight across charts.
- Logarithmic and symlog scales — data spans many orders of magnitude but isn't strictly positive.
- Different series may have different X subsets (sparse logging, early termination).

## Targets

- 100k points per chart is the main benchmark, working for either 100+ series × 1000+ points or 1000+ series × 100+ points.
- 1M-point chart should still work reasonably.
- 100+ charts loaded with 100+ visible, with shared interactions, on the same page.
- Performance ≥ uPlot (without uPlot's decimation, which misrepresents the data) on initial draw, redraw, and highlight.
- Zero deps; React is a peer dep for the React wrapper.

## Marks

- **Lines**: configurable stroke width, color, dash pattern.
- **Points**: degenerate single-point lines with separate dot size.
- **Bands**: filled areas between two series. API supports both "two named series" and Dygraphs-style `customBars` triplets.
- Drawing order per chart: bands → lines → points → highlighted bands → highlighted lines → highlighted points. Series order is the input order.
- Highlighted marks redraw on the overlay with optional border. Default border for lines/points = plot background color; for (semi-transparent) bands = the full color.

## Data

- Inputs: `number[]`, `Float64Array`, `Float32Array`, `number[][]` (row-oriented). Random access required — no generators.
- Inputs assumed sorted by X; out-of-order is unspecified.
- Independent X values per series (not shared like in uPlot/Dygraphs).
- Internally copied into TypedArrays, possibly normalized (see Performance below). Float32 likely sufficient post-normalization.
- Missing/NaN: skip and connect across (uPlot-style); per-series override is a later refinement.
- Bands draw each edge independently; longer edge is clipped/interpolated to the shorter edge's range.
- Empty data renders axes with a fallback range (e.g. `[0, 1]`); no built-in loading state.
- Series identified by stable ids — used as cache key so add/remove doesn't invalidate everything.
- Live/append data works via full redraws; no streaming-specific optimization.

## Scales

- Linear, log, symlog. Log is implemented as a special case of symlog, so non-positive values are handled uniformly.
- Symlog parametrization (linear-bridge size in data and screen coords) auto-derived from data; manual override available.
- Time scales: linear-only. Date inputs accepted alongside numeric timestamps. Browser timezone.
- Any finite range supported, including ranges where `max - min > Number.MAX_VALUE` (handled via normalization).
- Single-value ranges expand for context. Reversed-range behavior TBD (reverse-render vs. auto-sort vs. degenerate).
- Auto-fit on both axes with px or %-based padding. Y auto-fit stays active when zoomed on X. Auto-fit can only narrow the last user-set Y range, never widen it.
- Multiple Y-axes: planned, not in the initial cut.

## Axis labels

- ≥2 labels per axis when width allows; never repeated, never overlapping, never overflowing.
- Tick placement matches displayed label precision exactly — no rounding except float quirks and sub-pixel collapse.
- Aligned to nice decimals when feasible.
- Y-axis width adaptive to label width; X-axis label height fixed (angled X labels: future extension).
- Number formatting (precision, scientific threshold) auto-derived from chosen ticks. Per-axis formatter override available.
- Per-value label injection (e.g. highlight first X) while preserving the constraints above.
- Time-based ticks/labels are best-effort and may have quirks (repeats, overlaps) until polished.
- Locale separators / a11y: out of scope for now.

## Interactions

- Built-in zoom (mouse drag rectangle).
- Zoom respects float precision: at minimum, fail silently or nudge the range; ideally reject with a message and show the clamped range in the zoom rectangle.
- Hover line/point highlight; highlighting a line is not constrained to defined points — interpolate `y` at hovered `x`; if no series has data there, fall back to the closest `x` with any data.
- Programmatic highlight, multiple independent marks.
- Built-in tooltip (basic). May get split into a separate connected component later.
- Crosshair (uPlot-style) and X-value line (Neptune-style) available as options.
- Shared zoom + highlight via a controller (likely React context with a Provider). Reactive only — does **not** synchronize initial axis ranges; that's the consumer's job (passed via props/initial state) to avoid blink/load storms during async loading.
- Some legend; series-toggle is not a near-term feature.
- Pinch/pan zoom on touch, partial zoom-out (×2), panning, range selection, animations: later.
- Callbacks: hover, zoom, zoom-reset, plus event pass-through. Payloads include data↔screen coord conversions.
- React `ref` may expose a more imperative interface (TBD).

## Architecture

- Framework-agnostic core with internal caching/diffing; thin React wrapper forwards props. Trade-off accepted: cleaner React story, harder to expose a clean imperative non-React API.
- React-style memoization with cache keyed by series ids. Mutable inputs may have a perf penalty or be unsupported if they conflict with this model.
- Theming target: CSS variables for general styling, with JS config only as override. Canvas-rendered parts need their own escape hatch.

## Performance techniques

- **Path2D caching.** Building a Path2D and stroking it is faster than direct canvas calls (especially on Firefox), even single-use. Cache stored in data coords normalized to the configured zoom (not the displayed range, which would flip on every resize and margin change); applied via canvas transform at draw time; invalidated only on large (order-of-magnitude) zoom changes.
- **Data normalization.** Required so we can render sub-ranges narrower than float64 precision allows when scaled to screen coords. Likely doubles as the internal storage format.
- **Canvas stacking.** Two stacked canvases (main + overlay). Highlighted marks are drawn twice (once normal, once highlighted on the overlay). Assumes highlighted set ≪ total set; degenerates when not — accepted.
- **DOM**, not canvas, for crosshair, zoom rectangle, and likely axes/labels.
- **Virtualization** for off-viewport charts.
- **Canvas size handling**: auto-handle DPR and `ResizeObserver` (consumer can opt out); cap raster size below the browser limit; verify allocation and reduce raster size on failure.
- **OffscreenCanvas / Workers**: maybe later. TypedArray transfer is the only fast IPC path; communication cost likely eats the win.
- **WebGL**: probably not worth it. 16-contexts-per-domain limit forces shared-context tricks; native support is 1px-only lines and no dash patterns.

## Robustness

- Type-correct config never crashes. Non-finite numbers handled gracefully. Inconsistent inputs: behavior unspecified.
- Clearly malformed inputs throw with descriptive messages.

## Out of scope

- SSR (browser-only; React wrapper is a no-op on server).
- Legacy browsers; modern evergreen only.
- Full a11y.
- Auto-sync of axes between charts on initial load. Sync reacts only to user (and possibly programmatic) interactions.
- Plugins, full theming, customized interactions, animations, range selection, panning, extra markers — until the library is well past its core scope.
- Bar/pie/other chart kinds, categorical X axis.
- Streaming-specific optimization.
- CommonJS output (ESM-only).
- Bundle size target (zero deps keeps it modest by default).

## Performance benchmarks

Reference: developer laptop (Neptune's user base has beefy machines). Targeting "max this machine can give us" rather than worst-case.

≫60 FPS for highlight/resize/interact on:

- 1 fullscreen × 20 lines × 1000 points.
- 10 small × 20 lines × 1000 points.

>30 FPS on:

- 1 fullscreen × 1000 lines × 100 points.
- 1 fullscreen × 1000 lines × 1000 points.
- 10 small × 1000 lines × 100 points.
- 10 small × 100 lines × 1000 points.
- 10 small × 100 lines × 300 points.
- 100 small × 100 lines × 300 points.

Plus each of the above with extra off-viewport charts loaded. Test data is pre-generated; in-JS generation is too slow.

## Testing

Visual regression via headless canvas, preferring cairo-backed over a full browser. Diff noise mitigated by color quantization, downscaling, disabling antialiasing — expected to need iteration; browser-based may end up necessary.
