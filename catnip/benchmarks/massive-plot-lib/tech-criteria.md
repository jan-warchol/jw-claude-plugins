# Key Points

## Must mention

- Canvas-based, performance-focused library for massive data; not a generic charting tool
  (decimation and initial axis sync pushed to consumer)

- Performance target ≥ uPlot, benchmarked without uPlot's decimation
  FULL: names uPlot as the benchmark bar AND notes that uPlot-with-decimation is excluded from the comparison
  PARTIAL: names uPlot anywhere as a performance reference (e.g. "uPlot-level throughput", "≥ uPlot", "matches uPlot") without the decimation-fairness point
  SILENT: states its own numeric perf targets but never mentions uPlot

- Independent X values per series (key divergence from uPlot/Dygraphs)

- Shared zoom+highlight reactive-only — does NOT sync initial axis ranges, with rationale
  (async-load blink/storm on data load)

- Path2D cache stored in zoom-normalized data coords; applied via canvas transform at draw time;
  invalidated only on large (order-of-magnitude) zoom changes
  FULL: caches in a normalized/rescaled coordinate space (e.g. [0,1] over the data window) + draw-time transform
  PARTIAL: caches in plain (un-normalized) data coords + draw-time transform — missing element, not a contradiction; score +5, never negative
  CONTRADICTS: caches in display/pixel coords; argues against data-space caching

- Stable caller-assigned series IDs as path cache keys; adding/removing one series does not
  invalidate others' cached paths
  CONTRADICTS: cache keyed on array index/insertion order; spec explicitly flushes entire cache on any single add/remove
  Secondary: listing cache-invalidation triggers (e.g. "invalidated on data change or series add/remove") still AGREES — naming when entries rebuild ≠ flushing all on add/remove

- Data normalization to handle ranges where max−min > Number.MAX_VALUE


## Should mention

- Canonical use case: ML training metrics dashboards with 1M+ points server-aggregated to ≤100k per
  chart

- Main benchmark: 100k points per chart, across both series/point regimes
  FULL: states the 100k-per-chart figure AND acknowledges both regimes (few-series-many-points e.g. 100+ series × 1k pts, AND many-series-few-points e.g. 1k+ series × 100 pts)
  PARTIAL: states 100k-per-chart with only one regime, or with neither (dual-regime is a required element, not parenthetical)

- Concrete FPS benchmark scenarios with specific series/point-count configurations
  FULL: explicit small/large FPS split (e.g. ≫60 FPS small-scale, >30 FPS large-scale) tied to specific configs; ms budgets tied to specific configs count equally
  PARTIAL: numeric targets (FPS or ms) tied to specific configs, without the small/large split
  SILENT: bare FPS/perf number not tied to any specific point-count/series configuration

- Symlog parametrization (linear-bridge size in data and screen coords) auto-derived from data —
  a smart default that does not require the consumer to supply parameters

- Symlog parametrization manual override available as fallback
  CONTRADICTS: explicitly offering no manual override / "no manual tuning"

- Tick placement must match displayed label precision exactly (no rounding beyond float quirks)
  CONTRADICTS: rounded SI/compact labels (e.g. 1.2M, 3.4B)

- Numeric axis labels robust for any range: ≥2 labels, no repeated labels, no overlap, no overflow;
  Y-axis width adaptive to required label width

- Auto-fit Y stays active under X-zoom; can only narrow last user-set Y range, never widen

- NaN/missing values: skip and connect across (uPlot-style) — line continuity, distinct from markers
  CONTRADICTS: pen-lift / visible gap / break at NaN

- Non-finite value markers: NaN and ±Inf both visibly represented on the chart; representation
  ideally configurable (ignore / dedicated marker / edge-clipped line to ±∞)
  FULL: both NaN and ±Inf represented as non-finite indicators; opt-in/configurable representation earns the same credit as default
  PARTIAL: only one of NaN or ±Inf represented

- Integrated/built-in tooltip showing hovered value(s) or all values at hovered X (at least basic;
  not deferred entirely to the consumer)

- Canvas stacking: main + overlay canvas; highlighted marks drawn twice; design assumes highlighted
  set ≪ total
  FULL: describes the main+overlay (two-canvas) stack
  Secondary: "drawn twice" and "highlighted ≪ total" are secondary — a spec describing the two-canvas stack earns FULL without them

- Framework-agnostic rendering/computation core with thin declarative React wrapper
  FULL: framework-neutral rendering/computation engine + React as a thin wrapper
  PARTIAL: framework-neutral controller/state only; rendering core is React-only or not clearly separable
  SILENT: entirely React (even the controller is a React hook) with no neutral element — being React-only is NOT a contradiction
  CONTRADICTS: explicitly rejects / argues against a framework-agnostic core

- Input formats: number[], Float32Array, Float64Array, number[][] row-oriented; random access
  required; sorted by X assumed
  FULL: offers the full multi-format surface (number[] plus typed arrays, ideally including row-oriented)
  PARTIAL: accepts several listed types but omits one, without rejecting any
  CONTRADICTS: explicitly requires a single typed array and rejects number[] (e.g. "Float64Array required (not number[])")

- Zoom float precision handling (fail silently or nudge at minimum; ideally reject with message and
  show clamped range in zoom rectangle)

- Callbacks (hover, zoom, zoom-reset, event pass-through) with data↔screen coordinate conversions
  in payloads

- Decimation out of scope — consumer's responsibility
  CONTRADICTS: built-in / automatic core decimation

- Zero deps, ESM-only, React as peer dep, browser-only (no SSR)

- WebGL rejected (16-context-per-domain limit; no native wide lines or dash patterns)

- Log scale implemented as a special case of symlog (not a separate code path); handles non-positive
  values uniformly
  CONTRADICTS: separate log code path; explicitly "log is not a degenerate symlog"


## Could mention

- Bands: two-series API or Dygraphs customBars triplets; edges drawn independently (longer edge
  clipped to shorter's range)
  Secondary: clip/clamp behavior alone does not flip the stance to a contradiction; providing either band API earns the point

- Drawing order: bands → lines → points → highlighted bands → highlighted lines → highlighted points

- Highlight border defaults: bg color for lines/points; full color for (semi-transparent) bands

- Time scales linear-only; best-effort at V0 (repeats/overlaps acceptable); browser timezone

- Date inputs accepted alongside numeric timestamps

- Empty data → fallback axis range (e.g. [0,1]); no built-in loading state

- Live/append data = full redraws; no streaming-specific render optimization
  CONTRADICTS: incremental/streaming render path that avoids the full redraw
  Secondary: copying appended data into buffers then invalidating the path cache still = full redraw (AGREES); deferring a dedicated streaming render path also AGREES

- Float32 internal storage post-normalization (optional optimization; about internal storage, not
  input type)
  SILENT: choosing Float64 for internal storage — declining an optional optimization is not a contradiction
  Secondary: a spec that fixes an input type but is silent on internal storage is also SILENT here

- OffscreenCanvas/Workers deferred (TypedArray IPC transfer cost likely eats the gain)

- DOM (not canvas) for crosshair, zoom rectangle, and axes/labels

- Programmatic highlight with multiple independent marks

- Hover highlight: interpolated y at hovered x; fallback to closest x where any series has data
  CONTRADICTS: snapping to nearest defined data point instead of interpolating

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

- Automatic statistical outlier detection (IQR/percentile flagging, outlier rings) — reference
  relies on visual spotting plus non-finite markers, not computed outliers

- Bundle-size target/budget — reference explicitly sets none ("No target")
