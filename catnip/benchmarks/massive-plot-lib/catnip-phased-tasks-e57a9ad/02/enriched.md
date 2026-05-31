# Spec: Fast Canvas-Based Plotting Library for ML Dashboards

## Objective

Build a high-performance, zero-dependency, ESM-only plotting library for ML training dashboards. The library renders line, point, and band charts using the 2D Canvas API (no WebGL, no workers). It targets dashboards with 100+ simultaneously visible charts, each drawing up to 100k pre-aggregated data points across many series, with coordinated zoom/highlight across charts, log/symlog scales, and first-class handling of NaN/±Inf outlier markers.

Target performance envelope:
- Match or beat uPlot for raw draw throughput at 100k pts/chart (≤ 5 ms draw time on a mid-range 2023 desktop).
- Match or beat Dygraphs for interactive responsiveness: crosshair and zoom-rect updates must not drop frames at 60 Hz.

React is a peer dependency; the library exposes React components but ships no React code in the bundle itself.

**Assumption**: data is always pre-aggregated server-side before being passed to the library. The library never aggregates or decimates.

---

## Requirements

### Must do

- Render **line**, **point** (scatter), and **band** (filled area between two series) chart types on a 2D Canvas.
- Support up to **100k data points per chart** (e.g. 100 series × 1 000 pts, or 1 000 series × 100 pts) within the performance envelope above.
- Remain usable (no crash, degraded perf acceptable) with up to **1M data points per chart**.
- Support **100+ charts visible simultaneously** without degrading the page.
- Support **multiple series per chart**, each with its own independent X axis (series do not need to share X values or X domain).
- Provide **synced zoom and crosshair highlight** across an arbitrary subset of charts via a shared controller.
- Support **log scale** (positive values only) and **symlog scale** (all values including zero/negative); symlog is treated as a special case of log with auto-derived parameters.
- Mark **NaN** and **±Infinity** values visually (line gap + optional DOM marker at NaN sites; ±Inf clipped to axis edge with directional DOM marker).
- Expose stable **series/chart IDs** provided by the caller; used internally as cache keys.
- React component API with props-driven rendering: no imperative init/sync methods; shared controller is reactive-only (state in, callbacks out).
- Support **DPR-aware rendering**, **ResizeObserver**-driven re-layout, and **raster size capping** (configurable `maxRasterPixels`, default `4096 * 4096`).
- **Virtualize off-viewport charts**: release canvas pixels on scroll-out, restore on scroll-in.
- **DOM-based overlays** for crosshair, zoom-rect, and axis ticks/labels; canvas used only for data pixels.
- Cache rendered **Path2D objects** in zoom-normalized coordinates; invalidate on data or size change. Path2D cache is bounded by an LRU with a configurable `maxCachedPaths` limit (default: 500 paths).
- Normalize input data arrays internally to typed arrays; do not mutate caller data.
- No runtime dependencies; ESM only.

### Must not do

- Must not decimate or subsample data.
- Must not use WebGL, OffscreenCanvas, or Web Workers for rendering.
- Must not support SSR / Node.js environments.
- Must not include accessibility features, animations, theming systems, or plugin hooks.
- Must not render bar, pie, or categorical chart types.
- Must not ship CommonJS output.

---

## Solution

### Rendering architecture

Each chart manages a **stacked layer model**:

1. **Main canvas** (2D): draws all series paths. Redrawn on zoom/pan/data change.
2. **Highlight canvas** (2D, `position: absolute` on top): draws the hover state — the focused series redrawn at full opacity, all other series dimmed to 30%, plus a filled dot at the crosshair intersection point. Redrawn only when hover state changes, avoiding full redraws for crosshair movement.
3. **DOM overlay** (`position: absolute`, pointer-events: none): axis ticks/labels, crosshair line (`<div>` CSS-transformed), zoom-rect (`<div>` with border).

Stacking order (bottom to top): main canvas → highlight canvas → DOM overlay.

Canvas pixel size = `width × DPR` by `height × DPR`; CSS size = `width × height`. If `width × height × DPR² > maxRasterPixels`, DPR is clamped to fit. The raster cap clamps silently; a `onRasterCap` callback prop is available for callers that want to log or display a warning.

### Axis layout

Each chart reserves a fixed margin area for axes (default: 48 px left for Y labels, 24 px bottom for X labels, 8 px top/right padding). The plot area (canvas + stacked layers) fills the remaining space. Margin sizes are configurable props. The library generates tick values and labels internally using a "nice numbers" algorithm (linear: Wilkinson-style; log: powers of 10; symlog: powers of 10 on each side of zero plus a zero tick).

### Path2D caching

Series paths are cached per `(chartId, seriesId, dataVersion)` in **zoom-normalized coordinates** where the full X/Y data range maps to `[0, 1]`. On zoom/pan the canvas context transform (`ctx.setTransform`) maps the visible sub-range of normalized space to canvas pixels — no path recomputation needed. `dataVersion` is a monotonic counter incremented on data prop change. The LRU evicts least-recently-used entries when `maxCachedPaths` is exceeded.

Path generation: `Float64Array` → typed coordinate buffer → single `Path2D` construction pass. For band charts, the forward pass of the upper bound and the reverse pass of the lower bound are joined into one closed `Path2D`.

### Point chart rendering

At high point densities, individual circle calls per point are prohibitively slow. The point chart renders each point as a 2×2 pixel rectangle (`ctx.fillRect`) unless `pointRadius` is explicitly set to > 1, in which case a `Path2D` arc loop is used. This keeps 100k-point scatter plots within the performance budget. `pointRadius` defaults to 0 (2×2 px rect).

### Data normalization

Input arrays are copied to `Float64Array` (X) and `Float32Array` (Y) on first assignment. NaN and ±Infinity are preserved in the typed arrays. During rendering:
- **NaN**: `moveTo` (line break) + optional diamond DOM marker at the gap x-position.
- **+Inf**: Y clipped to top axis edge + upward-arrow DOM marker.
- **-Inf**: Y clipped to bottom axis edge + downward-arrow DOM marker.

**Live / streaming data**: incremental append (passing a longer array with the same series ID) is supported — the library detects the length increase, copies only the new tail, increments `dataVersion`, and invalidates the path cache. Full replacement (new data with the same ID) follows the same invalidation path. Streaming is thus in scope but append batching is the caller's responsibility.

### Scale system

- **Linear**: identity.
- **Log**: `log10(v)`; non-positive values treated as NaN with a console warning.
- **Symlog**: `sign(v) × log10(1 + |v| / C)`. `C` is auto-derived as `max(|finite v|) / 1000` per data change. Callers may override `C` via a `symlogThreshold` prop. `B` (scale factor) is 1 and not exposed.

Scale type is a per-axis prop (`xScale`, `yScale`). Each series carries its own `xScale`; Y scale is shared per chart.

### Zoom coordinate semantics

The controller's `zoomRange` is stored in **normalized [0, 1] space** relative to each series' own X extent. This is the only coherent option when series have independent X domains (e.g., series A covers steps 0–10 000, series B covers steps 5 000–50 000). A zoom to `[0.2, 0.6]` means "show the middle 40% of each series' own range." Charts in the same controller group that share X domains will therefore zoom identically in data space; charts with different domains zoom proportionally. Crosshair `highlightX` is also in normalized X space; each series converts it to its own data coordinate for nearest-point lookup.

*Assumption*: users of the sync controller understand that zooming aligns proportional position, not absolute value, when series have mismatched X domains. This should be documented prominently.

### Shared controller (zoom/highlight sync)

```ts
const controller = usePlotController();
// controller.zoomRange: [number, number] | null  (normalized [0,1], null = full)
// controller.highlightX: number | null           (normalized X position)
// controller.highlightSeriesId: string | null
```

The controller is purely reactive: no `init()` or `sync()`. Charts read state from React context on render; interactions call `onZoomChange` / `onHighlightChange` callbacks that the caller wires to their own state. This prevents async blink storms where charts race to initialize shared state on mount.

Zoom: pointer-down + drag → zoom-rect tracks drag → pointer-up fires `onZoomChange`. Reset zoom: double-click fires `onZoomChange(null)`. Pan: modifier key (default: Alt) + drag → adjusts range.

### Viewport virtualization

`IntersectionObserver` (threshold: 0) watches each chart root. On exit: canvases set to `width=0 height=0` (releases GPU texture memory); Path2D cache entries are retained (CPU memory only, bounded by LRU). On entry: canvases re-allocated, current controller zoom state read synchronously before first paint, then full redraw. No async gap between zoom state restore and first paint.

### React API

```ts
const controller = usePlotController();

<PlotControllerProvider controller={controller}>
  {/* Line chart, two series with independent X */}
  <Plot
    id="loss-chart"
    width={600} height={300}
    chartType="line"
    yScale="log"
    series={[
      { id: "train", x: Float64Array, y: Float32Array, color: "#4f8ef7", xScale: "linear" },
      { id: "val",   x: Float64Array, y: Float32Array, color: "#f74f4f", xScale: "linear" },
    ]}
    onZoomChange={setZoom}
    onHighlightChange={setHighlight}
  />

  {/* Band chart: lower/upper bounds paired by id */}
  <Plot
    id="ci-chart"
    chartType="band"
    series={[
      { id: "mean",  x: Float64Array, y: Float32Array, color: "#4f8ef7" },
      { id: "upper", x: Float64Array, y: Float32Array, bandWith: "lower", bandColor: "rgba(79,142,247,0.2)" },
      { id: "lower", x: Float64Array, y: Float32Array },
    ]}
  />
</PlotControllerProvider>
```

For band charts, a series with `bandWith: "<otherId>"` pairs with the named sibling series to form the filled band. The paired series' paths are combined into one closed `Path2D` filled with `bandColor`. Both bounding series are also drawn as lines.

`id` on `<Plot>` and each series object must be stable; changing an `id` is equivalent to a full series replacement.

### Build / distribution

- Bundled with **Rollup** or **tsup** → single ESM `.js` + `.d.ts`.
- `peerDependencies`: `react`, `react-dom` ≥ 18.
- `dependencies`: none.
- TypeScript source, strict mode. Tree-shakeable by chart type.

---

## Alternative solutions considered

### WebGL
Rejected. ~16-context browser limit; a 100-chart dashboard exceeds it immediately, causing silent software fallback. No native wide lines or dashes — both require custom geometry, negating simplicity gains.

### OffscreenCanvas + Web Workers
Rejected. At 100k points, `postMessage` serialization cost (~0.5–2 ms/transfer) is comparable to the entire draw budget (~2–5 ms). Path2D objects are not transferable. Main-thread Path2D caching is the better trade-off.

### Decimation / downsampling
Rejected. Data is pre-aggregated server-side; the library must render all points to preserve outlier visibility.

### SVG
Rejected. SVG DOM per point at 100k+ scale causes prohibitive memory and layout cost.

---

## Out of scope

- SSR / Node.js environments.
- Accessibility (ARIA, keyboard nav, screen reader).
- Animations and transitions.
- Plugin / extension system; CSS variable theming.
- Bar, pie, categorical charts.
- CommonJS output.
- Client-side data aggregation or decimation.
- Touch gestures (pinch-to-zoom) — may be added later.
- Export to PNG/SVG.

---

## Uncertainty

1. **Path2D cache hit rate under live data**: frequent streaming updates invalidate cache entries rapidly. The LRU cap (`maxCachedPaths`) mitigates memory growth but does not restore cache hits. If streaming is latency-critical, a ring-buffer append model (extending the Path2D rather than rebuilding) could help, but this is complex and deferred.

2. **Symlog `C` heuristic**: `max(|v|) / 1000` can visually compress data when extreme outliers dominate. A percentile-based fallback (e.g. 99th-percentile / 1000) or an explicit `symlogThreshold` override prop (already in the design) may be necessary in practice.

3. **ResizeObserver overhead at 100+ charts**: one observer per chart vs. one shared observer with a WeakMap of callbacks. Should benchmark at 200+ charts; shared observer is likely faster and is a drop-in change.

4. **Raster cap on high-DPR displays**: silent DPR clamping produces blurry charts. The `onRasterCap` callback gives callers a signal; whether a visual indicator should be built in is deferred.

5. **Normalized zoom UX when X domains differ substantially**: proportional zoom is technically coherent but may confuse users who expect time-aligned zoom. Dashboard-level documentation and potentially a "lock to time domain" mode may be needed.
