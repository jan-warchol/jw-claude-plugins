# Spec: Fast Canvas-Based Plotting Library for ML Dashboards

## Objective

Zero-dependency, ESM-only plotting library for ML training dashboards. Renders line, point, and band charts via the 2D Canvas API (no WebGL, no workers) for dashboards with 100+ simultaneous charts, ≤100k pre-aggregated pts/chart, coordinated zoom/highlight, log/symlog scales, and NaN/±Inf outlier markers.

Performance targets: ≤5 ms draw time at 100k pts/chart (mid-range 2023 desktop); crosshair/zoom-rect updates at 60 Hz without frame drops. React ≥18 is a peer dependency.

**Assumption**: data is always pre-aggregated server-side; the library never aggregates or decimates.

---

## Requirements

### Must do

- Render **line**, **point** (scatter), and **band** (filled area between two series) on a 2D Canvas.
- Handle ≤100k pts/chart within the performance envelope; remain usable (no crash) up to 1M pts/chart.
- Support 100+ simultaneously visible charts without page degradation.
- Multiple series per chart, each with an **independent X axis** (independent values and domain).
- **Synced zoom and crosshair highlight** across arbitrary chart subsets via a shared controller.
- **Log scale** (positive values only) and **symlog scale** (all values); symlog auto-derives its linear threshold `C`.
- **NaN/±Inf markers**: line gap + optional DOM diamond at NaN; ±Inf clipped to axis edge with directional DOM arrow.
- Caller-provided stable **series/chart IDs** used as cache keys internally.
- **Props-driven React API**: no imperative init/sync; controller is reactive-only (state in, callbacks out).
- **DPR-aware rendering**, **ResizeObserver** re-layout, configurable **raster cap** (`maxRasterPixels`, default `4096×4096`).
- **Virtualize off-viewport charts**: release canvas pixels on scroll-out, restore on scroll-in.
- **DOM overlays** for crosshair, zoom-rect, and axis ticks/labels; canvas for data pixels only.
- **Path2D cache** in zoom-normalized coords; LRU-bounded (`maxCachedPaths`, default 500); invalidate on data/size change.
- Copy input arrays to typed arrays internally; never mutate caller data.

### Must not do

- Decimate or subsample data.
- Use WebGL, OffscreenCanvas, or Web Workers.
- Support SSR / Node.js.
- Include a11y, animations, theming, or plugin hooks.
- Render bar, pie, or categorical charts.
- Ship CommonJS output.

---

## Solution

### Rendering architecture

Three stacked layers per chart (bottom to top):

1. **Main canvas** — all series paths; redrawn on zoom/pan/data change.
2. **Highlight canvas** (`position: absolute`) — hover state only: focused series at full opacity, others at 30%, filled dot at crosshair intersection. Redrawn on hover change only, not on every crosshair move.
3. **DOM overlay** (`position: absolute`, pointer-events: none) — axis ticks/labels, crosshair `<div>` (CSS transform), zoom-rect `<div>` (CSS border).

Canvas pixel size = `width×DPR` by `height×DPR`; CSS size = `width×height`. If `width×height×DPR² > maxRasterPixels`, DPR is clamped silently; `onRasterCap` callback prop notifies callers.

### Axis layout

Fixed margins (defaults: 48 px left for Y labels, 24 px bottom for X, 8 px top/right); all configurable props. The library generates tick values/labels internally: Wilkinson-style nice numbers for linear, powers-of-10 for log, powers-of-10 on each side of zero plus a zero tick for symlog.

### Path2D caching

Cache key: `(chartId, seriesId, dataVersion)`. Paths stored in **zoom-normalized space** (`[0,1]` over the full data range). On zoom/pan, `ctx.setTransform` maps the visible sub-range to canvas pixels — no recomputation. `dataVersion` increments on data change; LRU evicts on `maxCachedPaths` overflow.

Path generation: `Float64Array` → typed coord buffer → single `Path2D` pass. Band charts: forward pass of upper bound + reverse pass of lower bound → one closed `Path2D`.

### Point chart rendering

Default: 2×2 px rect per point (`ctx.fillRect`) — the only approach that fits within budget at 100k pts. When `pointRadius > 1`, a `Path2D` arc loop is used instead. `pointRadius` defaults to 0.

### Data normalization and streaming

Inputs copied to `Float64Array` (X) and `Float32Array` (Y) on first assignment. NaN/±Inf preserved; rendered as: NaN → `moveTo` gap + optional diamond marker; +Inf → clipped to top + upward arrow; -Inf → clipped to bottom + downward arrow.

**Incremental append** (same series ID, longer array): library copies only the new tail, increments `dataVersion`, invalidates path cache. Full replacement follows the same path. Append batching is the caller's responsibility.

### Scale system

- **Linear**: identity.
- **Log**: `log10(v)`; non-positive → NaN + console warning.
- **Symlog**: `sign(v) × log10(1 + |v| / C)`. `C` auto-derived as `max(|finite v|) / 1000` per data change; override via `symlogThreshold` prop. Scale factor `B = 1`, not exposed.

`xScale` is per-series; `yScale` is per-chart.

### Zoom coordinate semantics

`zoomRange` and `highlightX` are in **normalized [0, 1] space** relative to each series' own X extent. This is the only coherent model for independent X domains: `[0.2, 0.6]` means "middle 40% of each series' own range." Series sharing an X domain zoom identically in data space; mismatched-domain series zoom proportionally. Each series converts normalized `highlightX` to its own data coordinate for nearest-point lookup.

*Assumption*: users understand proportional (not absolute) alignment when X domains differ. Needs prominent documentation.

### Shared controller

```ts
const controller = usePlotController();
// zoomRange: [number, number] | null  — normalized [0,1]; null = full view
// highlightX: number | null           — normalized X
// highlightSeriesId: string | null
```

Purely reactive — no `init()` / `sync()`. Avoids async blink storms where mounting charts race to set shared state. Interactions: drag → `onZoomChange(range)`; double-click → `onZoomChange(null)`; Alt+drag → pan.

### Viewport virtualization

`IntersectionObserver` (threshold 0) on each chart root. On exit: canvases set to `0×0` (releases GPU memory); Path2D entries retained in CPU-side LRU. On entry: canvases re-allocated, controller zoom state read synchronously before first paint (no async gap).

### React API

```ts
<PlotControllerProvider controller={usePlotController()}>
  <Plot id="loss" width={600} height={300} chartType="line" yScale="log"
    series={[
      { id: "train", x: Float64Array, y: Float32Array, color: "#4f8ef7", xScale: "linear" },
      { id: "val",   x: Float64Array, y: Float32Array, color: "#f74f4f", xScale: "linear" },
    ]}
    onZoomChange={setZoom} onHighlightChange={setHighlight}
  />

  {/* Band: series with bandWith pairs with named sibling */}
  <Plot id="ci" chartType="band" series={[
    { id: "mean",  x: Float64Array, y: Float32Array, color: "#4f8ef7" },
    { id: "upper", x: Float64Array, y: Float32Array, bandWith: "lower", bandColor: "rgba(79,142,247,0.2)" },
    { id: "lower", x: Float64Array, y: Float32Array },
  ]} />
</PlotControllerProvider>
```

`bandWith` references a sibling series ID; the pair forms one closed `Path2D` filled with `bandColor`; both bounds also draw as lines. Changing any `id` is equivalent to a full replacement.

### Build

Rollup or tsup → single ESM `.js` + `.d.ts`. `peerDependencies`: `react`, `react-dom` ≥18. Zero `dependencies`. TypeScript strict mode. Tree-shakeable by chart type.

---

## Alternatives rejected

| Option | Reason |
|---|---|
| WebGL | ~16-context browser cap; 100-chart dashboard exceeds it. No native wide lines/dashes. |
| OffscreenCanvas + Workers | `postMessage` serialization (~0.5–2 ms) ≈ entire draw budget. Path2D not transferable. |
| Decimation | Hides outliers; data is already server-aggregated. |
| SVG | Per-point DOM nodes at 100k+ scale: prohibitive memory and layout cost. |

---

## Out of scope

SSR; accessibility; animations; plugins/theming; bar/pie/categorical charts; CommonJS; client-side aggregation/decimation; touch gestures (future); PNG/SVG export.

---

## Uncertainty

1. **Path2D cache under streaming**: frequent data updates invalidate entries; LRU bounds memory but not miss rate. Ring-buffer path extension could help for latency-critical streaming but is deferred.
2. **Symlog `C` heuristic**: outlier-heavy distributions may compress the bulk of data. `symlogThreshold` override is already available; a percentile-based default may prove necessary.
3. **ResizeObserver at 100+ charts**: per-chart observers vs. one shared observer + WeakMap. Shared observer is likely faster; benchmark before shipping.
4. **Raster cap UX**: silent DPR clamping blurs charts; `onRasterCap` callback available. Whether to render a built-in warning is deferred.
5. **Proportional zoom UX**: may confuse users expecting time-aligned zoom across mismatched X domains. A future "lock to absolute domain" mode may be needed.
