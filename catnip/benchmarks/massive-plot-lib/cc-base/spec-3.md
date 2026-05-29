# Canvas Plot — Technical Specification

**Version:** 0.1.0-draft  
**Status:** Pre-implementation  
**Scope:** ESM-only, React peer dependency, zero runtime dependencies

---

## 1. Goals and Non-Goals

### Goals

- Render line, point, and band (area-between) series at ≤100 k points per chart with no perceptible
  frame drops on a mid-range laptop (target: 60 fps pan/zoom, <16 ms initial render).
- Support dashboards with 100+ charts simultaneously loaded and visible.
- Accept pre-aggregated server data; 1 M points/series is a plausible total data-set per series,
  displayed through zoom-level selection by the caller.
- First-class ML training-dashboard UX: outlier hunting, NaN/±Inf anomaly markers, synchronized zoom
  and crosshair highlight across all charts.
- Log and symlog axes with auto-derived parameters; independent X axis per series.
- Match or exceed uPlot throughput; match Dygraphs responsiveness.

### Non-Goals (explicitly out of scope)

- Server-side rendering (SSR / React Server Components).
- Accessibility (ARIA roles, keyboard navigation, screen-reader text).
- Plugins, theming API, animations/transitions.
- Bar, pie, scatter-matrix, or categorical chart types.
- CommonJS output; consumers must use ESM.
- WebGL rendering (16-context-per-page browser limit; no wide-line or dash-pattern support in WebGL
  without heavy shaders; driver instability on Linux/Mesa).
- OffscreenCanvas + Worker rendering (serialized ImageBitmap IPC round-trip exceeds cost of direct
  canvas rasterisation for incremental redraws; eliminates synchronous hit-testing).

---

## 2. Performance Model

### Budget allocation (per chart, 1920 × 400 px canvas, 100 k pts)

| Phase                                             | Budget     |
| ------------------------------------------------- | ---------- |
| Data → screen-space transform                     | ≤2 ms      |
| Path2D construction (first render or zoom change) | ≤6 ms      |
| `ctx.stroke()` / `ctx.fill()`                     | ≤4 ms      |
| Composite + highlight overlay                     | ≤2 ms      |
| **Total frame**                                   | **≤16 ms** |

Zoom-stable redraws (pan only, no scale change) must not rebuild Path2D objects. Highlight-only
redraws (crosshair move) must not touch the main canvas.

### Multi-chart budget

With 100+ charts, at most the **viewport-visible** set is actively rasterised. Off-viewport charts
are virtualized (placeholder `<div>` preserving layout height; canvas is detached). The scheduler
serializes heavy redraws across frames using a priority queue keyed by viewport proximity.

---

## 3. Architecture

### 3.1 Canvas Stack (per chart)

Each chart owns a stacking context with three layers:

```
┌─────────────────────────────────┐
│  [3] DOM overlay (position:abs) │  crosshair, zoom-rect, tooltip anchor
│  [2] Highlight canvas           │  series highlight, hover glow  (cleared every frame)
│  [1] Main canvas                │  series paths, fills           (cleared on data/zoom change)
│  [0] Axes DOM (position:abs)    │  tick labels, grid lines       (React-rendered, CSS transforms)
└─────────────────────────────────┘
```

**Why separate highlight canvas?** The crosshair and per-point glow update at pointer frequency
(~120 Hz on high-refresh displays). Re-rasterising the full series paths at that rate wastes CPU and
produces visible tearing on slow series. Clearing and re-drawing only the highlight layer costs <1
ms.

**Why axes in the DOM?** Tick labels are text; canvas text rendering is slow and produces blurry
sub-pixel glyphs at non-integer DPR. DOM text is GPU-composited by the browser for free. Axis layout
changes are rare (zoom change only) and CSS `translateX`/`translateY` updates are compositor-thread
operations.

### 3.2 Device Pixel Ratio and Raster Cap

```
physicalWidth  = Math.round(cssWidth  * window.devicePixelRatio)
physicalHeight = Math.round(cssHeight * window.devicePixelRatio)
```

A **raster cap** is enforced: `physicalWidth × physicalHeight` is clamped to a configurable maximum
(default 4 M physical pixels per canvas, ~2048 × 2048 at DPR 1). Above this threshold the canvas
logical size is reduced proportionally. This prevents GPU texture upload stalls on HiDPI monitors
with very wide charts.

`ResizeObserver` watches the chart container. On size change: cancel any pending redraw, re-evaluate
the raster cap, resize both canvases atomically (avoids a single-frame blank), then schedule a full
redraw.

### 3.3 Path2D Cache

Path2D objects are cached in **zoom-normalised coordinates** — not in CSS pixels, not in data units.

**Zoom-normalised coordinate space:**

```
xNorm = (xData - xMin_view) / (xMax_view - xMin_view)   ∈ [0, 1]
yNorm = (yData - yMin_view) / (yMax_view - yMin_view)   ∈ [0, 1]
```

Paths are built in this unit space. At render time a single `ctx.setTransform(w, 0, 0, -h, 0, h)`
maps the unit square to the canvas pixel area (Y-axis flip included). This means:

- **Pan** without scale change → only `setTransform` changes, Path2D objects are reused.
- **Zoom level change** → cache is invalidated per affected series, paths are rebuilt on the next
  frame.

Cache key:
`seriesId + ":" + xMin_view.toFixed(6) + ":" + xMax_view.toFixed(6) + ":" + yMin_view.toFixed(6) + ":" + yMax_view.toFixed(6)`
— floats fixed to 6 decimal places in normalised space to prevent floating-point churn invalidating
the cache on imperceptible movements.

**LRU eviction:** cache is bounded at 200 Path2D entries (covers 100 charts × 2 series each with one
previous zoom level buffered). Eviction is approximate LRU via a generation counter.

### 3.4 Data Normalisation

Raw series data is accepted as typed arrays (`Float64Array` preferred; `Float32Array`, plain
`number[]` accepted with auto-conversion). On intake:

1. Scan for `NaN`, `+Infinity`, `-Infinity` — record indices into a `Uint32Array` of anomaly
   positions per series.
2. Compute `xMin`, `xMax`, `yMin`, `yMax`, `yFiniteMin`, `yFiniteMax` (ignoring non-finite values
   for scale computation).
3. Store the processed descriptor alongside the original typed array (no copy of the data itself).

Data normalisation runs once per `(seriesId, data)` pair. The result is memoised by reference
equality on the data array (stable reference = no re-scan). Callers are expected to pass stable
array references; a new array reference triggers re-normalisation.

### 3.5 Stacked Rendering Path (detailed)

```
frame():
  if (!inViewport) return                          // virtualized

  ctx_main.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0)

  if (pathCacheInvalid):
    clearMain()
    for series in chart.series:
      path = buildPath(series, viewTransform)       // zoom-normalised coords
      cache.set(cacheKey(series, view), path)

  // apply unit→pixel transform once
  ctx_main.setTransform(canvasW, 0, 0, -canvasH, 0, canvasH)

  for series in chart.series:
    path = cache.get(cacheKey(series, view))
    ctx_main.strokeStyle = series.color
    ctx_main.stroke(path)

  drawAnomalyMarkers(ctx_main, series)             // Inf/NaN, drawn directly (few)
  drawBandFill(ctx_main, ...)                      // if band series

highlight_frame():                                  // runs independently at pointer rate
  ctx_hl.clearRect(0, 0, canvasW, canvasH)
  if (hovered):
    drawCrosshairIntersections(ctx_hl)
    drawHighlightDots(ctx_hl)
```

---

## 4. Scale and Axis System

### 4.1 Linear Scale

Standard linear mapping. Tick generation uses a modified Wilkinson extended algorithm with a target
of 5–8 ticks, preferring round numbers.

### 4.2 Log Scale

Base-10 log scale. Constraint: **all data values in the view must be strictly positive**. If any
visible data point is ≤ 0, the axis silently promotes to symlog (see below) and emits a
`console.warn` with the series id.

Tick positions: powers of 10 within the view range, plus minor ticks at 2×, 5× multiples.

### 4.3 Symlog Scale

Symmetric log: continuous through zero, linear near zero, logarithmic away from zero.

```
symlog(x, C) = sign(x) × log10(1 + |x| / C)
```

**Auto-derivation of `C` (the linear threshold):**

```
C = 10 ^ floor(log10(|yFiniteMin| or |yFiniteMax| or 1)) × 0.01
```

This sets `C` to 1% of the order of magnitude of the data extremes, giving a narrow linear band
around zero that is invisible to the user while keeping the transition smooth. Callers may override
`C` explicitly.

Symlog is the **special case of log** exposed to callers: `scale: "log"` checks data sign; if any
finite value is ≤ 0, symlog is used with auto `C`. `scale: "symlog"` forces symlog regardless. There
is no separate `"log-strict"` mode — callers that need a hard error on non-positive data should
validate before passing.

Tick positions: `{-10^n, ..., -C, 0, C, ..., 10^n}` at the same power-of-10 intervals as the plain
log scale.

### 4.4 Independent X Axes Per Series

Each series carries its own `xValues: Float64Array`. There is no shared X axis on the chart — the
chart's X axis displays the **union range** `[min(all series xMin), max(all series xMax)]` as the
default view range. The X tick grid is shared (driven by the view range), but each series is mapped
independently: a point at `x = t` is placed at pixel position
`(t - viewXMin) / (viewXMax - viewXMin) * canvasW`.

This supports comparing series with different time grids (e.g., a run logged every 100 steps vs. one
logged every 500 steps) without resampling.

---

## 5. Anomaly Markers (NaN / ±Inf)

Anomaly markers are drawn **after** the series path on the main canvas. They are not Path2D cached
(anomalies are rare; marker drawing is O(anomalies), not O(points)).

| Anomaly     | Marker                                  |
| ----------- | --------------------------------------- |
| `NaN`       | Open circle, 4 px radius, series color  |
| `+Infinity` | Upward triangle at yMax, series color   |
| `-Infinity` | Downward triangle at yMin, series color |

Markers are drawn at the X position of the anomalous point. For `±Inf`, the Y position is clamped to
the top or bottom of the plot area.

A per-chart **anomaly summary** (counts by type) is accessible via the `ChartRef.anomalySummary()`
method, intended for display in a dashboard legend.

---

## 6. Shared Controller

The `PlotController` is a reactive state container. It does **not** hold a list of chart instances
nor does it call methods on them — charts subscribe to it. This avoids the "init sync" problem
(charts rendered at different times would miss initial state if the controller pushed state
imperatively).

```ts
// Controller state (observable)
interface ControllerState {
  viewRange: { xMin: number; xMax: number } | null; // null = each chart uses its own auto-range
  highlightX: number | null; // data-unit X for crosshair
  selection: { xMin: number; xMax: number } | null; // zoom-rect selection in progress
}
```

### 6.1 Subscription Model

Charts subscribe to `PlotController` via a React context. On each state change:

1. If `viewRange` changed → invalidate Path2D cache, schedule full redraw.
2. If `highlightX` changed → schedule highlight-only redraw (does not clear main canvas).
3. If `selection` changed → update DOM zoom-rect overlay only (no canvas redraw until selection is
   committed).

State changes are **batched within a single microtask** using a dirty-flag pattern. Multiple rapid
controller updates (e.g., wheel scroll producing 5 events in one frame) produce at most one redraw
per chart per animation frame.

### 6.2 No Synchronous Init Sync

Charts must produce correct output when mounted **after** the controller already has a non-null
`viewRange`. This is guaranteed because charts read controller state in their own render/effect, not
in a one-time registration call.

Async blink storms — a pattern where charts mounted in batches briefly render at default zoom before
snapping to the shared range — are prevented by: reading controller state synchronously during the
first `useLayoutEffect`, so the canvas is painted with the correct view range before the browser
composites the first frame.

### 6.3 Zoom Interaction

Wheel and pinch-zoom events on any chart update `controller.viewRange`. Drag creates a `selection`
rect; on pointer-up the selection is committed to `viewRange` and cleared. Double-click resets
`viewRange` to null (each chart auto-ranges independently).

All interaction handlers are attached to the DOM overlay layer (pointer events: none on canvases;
the overlay captures all events).

---

## 7. Virtualization

A single `IntersectionObserver` (threshold: 0) watches all chart container elements.

- **Entering viewport:** allocate canvases, run first render, attach pointer handlers.
- **Leaving viewport:** detach canvases from DOM (canvases are detached, not destroyed — kept in a
  pool of up to 20 canvas pairs for rapid re-mount). Clear the Path2D cache entries for this chart.
  Leave the container `<div>` in place to preserve scroll position and layout.
- **Pool exhaustion:** beyond 20 pooled canvas pairs, leaving-viewport charts destroy their
  canvases. Re-entering viewport charts create new canvases and perform a cold render.

The virtualizer coordinates with the redraw scheduler: when many charts enter the viewport
simultaneously (e.g., user jumps to bottom of page), renders are queued and spread across frames in
viewport-proximity order (nearest first).

---

## 8. React Integration

### 8.1 Component API

```tsx
// Controller — one per dashboard (or per synchronized group)
const ctrl = usePlotController()

<PlotController value={ctrl}>
  <Chart
    series={series}          // SeriesDescriptor[]
    height={300}             // css pixels; width = 100% of container
    xLabel="Step"
    yLabel="Loss"
    yScale="log"             // "linear" | "log" | "symlog"
    yScaleParams={{ C: 1e-4 }} // optional symlog override
    id="loss-chart"          // stable string; used as cache-key namespace
    onZoom={handleZoom}      // optional; fired after viewRange committed
  />
</PlotController>
```

```ts
interface SeriesDescriptor {
  id: string; // stable; used as Path2D cache key
  label: string;
  xValues: Float64Array; // sorted ascending
  yValues: Float64Array; // same length as xValues
  yLower?: Float64Array; // band lower bound (same length); if present, renders band
  color: string; // CSS color string
  lineWidth?: number; // default 1.5
  pointRadius?: number; // 0 = no points, default 0; >0 draws circles at each point
  dash?: number[]; // ctx.setLineDash pattern
}
```

### 8.2 usePlotController

```ts
function usePlotController(initial?: Partial<ControllerState>): PlotController;
```

Returns a stable `PlotController` instance. The instance is created once per component mount (not
per render). Calling `ctrl.setViewRange(...)` or `ctrl.setHighlightX(...)` triggers subscriber
re-renders via the subscription model described in §6.

### 8.3 ChartRef

```tsx
const ref = useRef<ChartRef>(null)
<Chart ref={ref} ... />

interface ChartRef {
  redraw(): void                          // force full redraw
  resetZoom(): void                       // clear viewRange for this chart
  anomalySummary(): AnomalySummary        // { nan: number, posInf: number, negInf: number } per series
  toDataURL(type?: string): string        // export main canvas
}
```

### 8.4 Peer Dependency

```json
{
  "peerDependencies": {
    "react": ">=18.0.0",
    "react-dom": ">=18.0.0"
  }
}
```

React 18 concurrent mode is supported. The library does not call `ReactDOM.render` and has no class
components. State updates that flow through the controller use `useSyncExternalStore` for tear-free
reads under concurrent rendering.

---

## 9. Series Path Construction

### 9.1 Line Series

```
path = new Path2D()
first = true
for i in 0..n-1:
  x = xNorm(xValues[i])
  y = yNorm(yValues[i])
  if isFinite(yValues[i]):
    if first or prevWasAnomalous:
      path.moveTo(x, y)
      first = false
    else:
      path.lineTo(x, y)
    prevWasAnomalous = false
  else:
    prevWasAnomalous = true   // gap in line; anomaly marker drawn separately
```

A `NaN` in `yValues` produces a **visible gap** (path break) rather than a line-to-zero or
interpolation. This is intentional: in training dashboards, a NaN often represents a diverged run or
a logging failure, and connecting through it would misrepresent the data.

### 9.2 Band Series

If `yLower` is provided, the band fill is rendered as a closed path:

```
path = new Path2D()
// forward pass: upper bound
for i in 0..n-1: path.lineTo(xNorm(x[i]), yNorm(yUpper[i]))
// backward pass: lower bound
for i in n-1..0: path.lineTo(xNorm(x[i]), yNorm(yLower[i]))
path.closePath()
ctx.fillStyle = colorWithAlpha(series.color, 0.15)
ctx.fill(path)
// then stroke the upper bound as a normal line series
```

Band and line paths share the same Path2D cache keying scheme.

### 9.3 Point Series

When `pointRadius > 0`, points are drawn **in a separate pass** after the line path. For datasets ≤
5000 visible points, individual `arc` calls are used. Above 5000 visible points, point rendering is
suppressed to avoid per-point arc overhead (the line itself communicates the density). The threshold
is per-series-in-view, not total points.

---

## 10. Outlier Hunting Aids

### 10.1 Out-of-Range Clip Indicators

When a data point exists but falls outside the current Y view range, a **clip indicator** is drawn
at the chart edge:

- Arrow pointing up (point above view) or down (point below view), at the corresponding X position.
- Drawn in series color with 60% opacity.
- Limit 20 indicators per edge to avoid clutter; if more than 20 out-of-range points exist, a
  summary count `"+N more"` is shown at the axis edge.

### 10.2 Highlight Nearest-Point

When `controller.highlightX` is set (crosshair active), the highlight canvas draws a filled dot at
the nearest data point on each series to `highlightX` (by X distance). A tooltip payload (series
label, x, y, formatted values) is emitted via `onHighlight` callback prop.

Nearest-point lookup: binary search on the sorted `xValues` array, O(log n), performed on
pointer-move. No precomputed spatial index needed.

---

## 11. Module Structure

```
src/
  controller.ts       PlotController, usePlotController, useSyncExternalStore bridge
  chart.tsx           <Chart> component, canvas lifecycle, ResizeObserver, virtualization
  renderer.ts         buildPath(), drawAnomalyMarkers(), drawBandFill(), highlight_frame()
  scales.ts           linearScale, logScale, symlogScale, tickGenerator, autoSymlogC()
  cache.ts            Path2D LRU cache
  data.ts             normaliseSeriesData(), anomaly scan, typed-array intake
  axes.tsx            Axes DOM component, tick label React rendering
  scheduler.ts        priority-queue redraw scheduler, frame batching
  types.ts            SeriesDescriptor, ControllerState, ChartRef, AnomalySummary, …
  index.ts            public re-exports
```

No barrel files that re-export everything — only the public API surface is exported from `index.ts`.

---

## 12. Build and Distribution

- **Bundler:** Rollup (or Vite library mode) producing a single ESM file with `.d.ts`.
- **Output:** `dist/index.js` (ESM), `dist/index.d.ts`. No CJS output.
- **Tree-shaking:** all internal modules use named exports; no side-effecting top-level code.
- **Bundle size target:** <30 kB minified + gzip (no fonts, no icon assets).
- **TypeScript:** strict mode, no `any`, `noUncheckedIndexedAccess` enabled.
- **Tests:** Vitest + `@testing-library/react` for component tests. Canvas mock via
  `jest-canvas-mock` (adapted for Vitest). Performance regression tests run synthetic 100 k-point
  series and assert rasterisation time against a stored baseline.

---

## 13. Open Questions / Future Work

_These are recorded here but explicitly not part of v0.1 scope._

1. **Decimation hook:** An optional caller-supplied
   `decimate(series, viewXMin, viewXMax, pixelWidth)` callback would allow the library to request
   pre-aggregated data for the current zoom level. The cache key scheme already accommodates this
   (zoom-normalised coords). Not implemented in v0.1; callers pre-aggregate server-side.

2. **Y-axis zoom:** Currently `viewRange` contains only X bounds; Y is always auto-ranged to the
   visible data. Explicit Y pan/zoom would be a natural addition.

3. **Series streaming:** Appending points to a live series requires re-running normalisation and
   invalidating the Path2D cache. A streaming-optimised path that only rebuilds the tail of the path
   is possible but deferred.

4. **Touch interaction:** Pan and pinch-zoom on mobile. The DOM overlay already captures pointer
   events; a touch-action: none CSS rule and `touch-start`/`touch-move` handlers would complete
   this.

5. **WebWorker pre-processing:** Despite the IPC cost argument against OffscreenCanvas, running the
   O(n) normalisation scan (anomaly detection, min/max) in a worker is viable since it produces only
   a small descriptor object, not an ImageBitmap. Deferred pending profiling evidence that
   normalisation is a bottleneck.
