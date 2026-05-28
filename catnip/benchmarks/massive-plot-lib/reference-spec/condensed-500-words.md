# Plot library spec

Fast canvas-based plotting for massive data; not generic. Consumer handles decimation and initial axis sync.

## Canonical use case

ML training dashboards: many charts × many series, 1M+ points/series aggregated server-side to ≤100k/chart. Drives: outlier-spotting across packs of similar series (why huge-N charts matter); NaN/±Inf markers as bug indicators; zoom to recover hidden values; synced zoom+highlight; log/symlog for many-OOM not-strictly-positive data; independent X per series.

## Targets

100k points/chart — 100+ × 1000+ or 1000+ × 100+; 1M still usable; 100+ charts loaded, 100+ visible. ≥ uPlot perf (without its data-misrepresenting decimation) on initial draw, redraw, highlight. Zero deps; React peer.

## Marks

Lines; points (single-point lines, separate dot size); bands (two series, or Dygraphs `customBars` triplets). Draw order: bands → lines → points → same highlighted on overlay. Highlight border: line/point = bg color; band = full color over its semi-transparent fill.

## Data

Inputs `number[] | Float{32,64}Array | number[][]`, random access, sorted by X. Copied to possibly-normalized TypedArrays (Float32 fine post-normalization). Stable series ids as cache keys (resilient to add/remove). NaN: skip-and-connect. Empty data → fallback-range axes, no loading state. Live append = full redraw.

## Scales & axes

Linear, log, symlog. Log = symlog special case, non-positives handled uniformly. Symlog params auto-derived, overridable. Time scales linear-only, browser timezone. Any finite range supported, including `max-min > Number.MAX_VALUE` (via normalization). Single-value ranges expand. Auto-fit both axes; Y auto-fit stays on under X-zoom, only narrowing the last user-set Y range.

Labels: ≥2/axis when width allows, never repeat/overlap/overflow; ticks match displayed precision exactly. Y width adaptive; X height fixed. Format auto-derived, per-axis override. Per-value label injection. Time labels best-effort.

## Interactions

Drag-rect zoom, float-precision-safe. Hover highlight: interpolated `y` at hovered `x` (not constrained to defined points), fallback to nearest `x` with data. Programmatic multi-highlight. Basic tooltip; optional crosshair / X-value line. Shared zoom+highlight controller (React context), **reactive only** — consumer supplies initial ranges because async-load blink storms. Basic legend. Callbacks expose data↔screen converters.

## Architecture

Framework-agnostic core with cache/diff, thin React wrapper. Clean imperative non-React API and CSS-variable theming: later.

## Performance techniques

- **Path2D cache** in zoom-normalized data coords (survives resize + small zoom via canvas transform), invalidated only on order-of-magnitude zoom changes.
- **Data normalization**, also the internal storage format.
- **Stacked canvases** (main + overlay) for cheap highlights; assumes highlighted ≪ total.
- **DOM** for crosshair, zoom rect, axes/labels.
- **Virtualize** off-viewport charts.
- Auto DPR + `ResizeObserver`; cap raster, downscale on alloc failure.
- **OffscreenCanvas/Workers, WebGL**: probably not worth it (IPC cost; 16-context limit, no native wide lines/dashes).

## Out of scope

SSR, legacy browsers, full a11y, auto-sync of initial axis ranges, plugins/theming/custom interactions, animations, image export, range selection, panning, bar/pie/categorical, CommonJS, bundle-size target.

## Benchmarks

Dev-laptop reference. ≫60 FPS on small mixes (1× or 10× charts, 20 × 1000). >30 FPS on harder mixes up to 100 × 100 × 300 and 1 fullscreen × 1000 × 1000. Each also with off-viewport charts. Pre-generated data.

## Testing

Visual regression via headless canvas (cairo preferred); diff noise via color quantization, downscaling, disabled AA.
