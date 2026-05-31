# Key Points

## Must mention

- Canvas-based, performance-focused library for massive data; not a generic charting tool
  (decimation and initial axis sync pushed to consumer)
- Performance target ≥ uPlot, benchmarked without uPlot's decimation (which misrepresents data)
- Independent X values per series (key divergence from uPlot/Dygraphs)
- Log scale as a special case of symlog (non-positive values handled uniformly)
- Shared zoom+highlight reactive-only — does NOT sync initial axis ranges, with rationale
  (async-load blink/storm on data load)
- Path2D cache stored in zoom-normalized data coords (not display coords), applied via canvas
  transform at draw time; invalidated only on large (order-of-magnitude) zoom changes
- Stable series ids as cache keys (add/remove doesn't invalidate all cached paths)
- Data normalization to handle ranges where max−min > Number.MAX_VALUE

## Should mention

- Canonical use case: ML training metrics dashboards with 1M+ points server-aggregated to ≤100k per
  chart
- Main benchmark: 100k points per chart (working for 100+ series × 1000 pts AND 1000+ series × 100
  pts)
- Concrete FPS benchmark scenarios (≫60 FPS small-scale, >30 FPS large-scale, specific
  series/point-count configurations)
- Symlog parametrization (linear-bridge size in data and screen coords) auto-derived from data;
  manual override available
- Tick placement must match displayed label precision exactly (no rounding beyond float quirks)
- Numeric axis labels robust for any range: ≥2 labels, no repeated labels, no overlap, no overflow;
  Y-axis width adaptive to required label width
- Auto-fit Y stays active under X-zoom; can only narrow last user-set Y range, never widen
- Hover highlight: interpolated y at hovered x; fallback to closest x where any series has data
- NaN/missing values: skip and connect across (uPlot-style) — line continuity, distinct from markers
- Non-finite value markers: NaN/±Inf represented on the chart (bug-hunting use case); representation
  ideally configurable (ignore / dedicated marker / edge-clipped line to ±∞)
- Integrated/built-in tooltip showing hovered value(s) or all values at hovered X (at least basic;
  not deferred entirely to the consumer)
- Canvas stacking (main + overlay); highlighted marks drawn twice; design assumes highlighted set ≪
  total
- Framework-agnostic core with thin declarative React wrapper
- Input formats: number[], Float32Array, Float64Array, number[][] row-oriented; random access
  required; sorted by X assumed
- Zoom float precision handling (fail silently or nudge at minimum; ideally reject with message and
  show clamped range in zoom rectangle)
- Callbacks (hover, zoom, zoom-reset, event pass-through) with data↔screen coordinate conversions in
  payloads
- Decimation out of scope — consumer's responsibility
- Zero deps, ESM-only, React as peer dep, browser-only (no SSR)
- WebGL rejected (16-context-per-domain limit; no native wide lines or dash patterns)

## Could mention

- Bands: two-series API OR Dygraphs customBars triplets; edges drawn independently (longer edge
  clipped to shorter's range)
- Drawing order: bands → lines → points → highlighted bands → highlighted lines → highlighted points
- Highlight border defaults: bg color for lines/points; full color for (semi-transparent) bands
- Time scales linear-only; best-effort at V0 (repeats/overlaps acceptable); browser timezone
- Date inputs accepted alongside numeric timestamps
- Empty data → fallback axis range (e.g. [0,1]); no built-in loading state
- Live/append data = full redraws; no streaming-specific optimization
- Float32 sufficient post-normalization; normalization likely doubles as internal storage format
- OffscreenCanvas/Workers deferred (TypedArray IPC transfer cost likely eats the gain)
- DOM (not canvas) for crosshair, zoom rectangle, and axes/labels
- Programmatic highlight with multiple independent marks
- Virtualization for off-viewport charts
- Canvas size handling: auto DPR + ResizeObserver; cap raster size; verify allocation; reduce size
  on failure
- Robustness contract: type-correct config never crashes; clearly malformed inputs throw with
  descriptive messages
- Visual regression via headless canvas (cairo-backed preferred); noise mitigation (quantization,
  downscaling, antialiasing off); pre-generated test data
- Multiple Y-axes planned, not in initial cut
- CSS variables preferred for styling (JS config as override); canvas-rendered parts need separate
  escape hatch
- Single-value (degenerate) ranges auto-expanded to include surrounding context
- Configurable line stroke width, color, and dash/stroke pattern
- Modern evergreen browsers only, last ~2 versions (no legacy-browser support)

## Must Not mention

## Should Not mention

- Automatic statistical outlier detection (IQR/percentile flagging, outlier rings) — reference relies
  on visual spotting plus non-finite markers, not computed outliers
- Bundle-size target/budget — reference explicitly sets none ("No target")
