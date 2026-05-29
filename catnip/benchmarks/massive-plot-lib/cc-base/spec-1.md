# Velox Plot — Technical Specification

**Version:** 0.1.0-draft  
**Status:** Pre-implementation  
**Scope:** Canvas-based, high-performance 2-D chart library for ML dashboards

---

## 1. Goals and non-goals

### 1.1 Goals

| Goal                                                                                   | Target                                        |
| -------------------------------------------------------------------------------------- | --------------------------------------------- |
| Render 100 k points per chart without decimation                                       | ≤ 16 ms first paint, ≤ 8 ms incremental frame |
| Support 100+ charts simultaneously visible in a single page                            | No browser jank during pan/zoom               |
| Handle 1 M points per series (pre-aggregated server-side, ≤ 100 k delivered per chart) | Smooth reactive updates                       |
| Synced zoom and crosshair across charts sharing a controller                           | Sub-frame latency                             |
| Outlier hunting: NaN / ±Inf rendered as explicit visual markers                        | Always visible regardless of scale            |
| Log and symlog axes, params auto-derived                                               | No manual `linThreshold` tuning required      |
| Independent X domain per series within a single chart                                  | Heterogeneous sampling rates                  |
| Zero runtime dependencies                                                              | Self-contained bundle                         |
| React peer (optional integration layer)                                                | Hooks + context, not required for core        |
| ESM-only output                                                                        | No CommonJS artifacts                         |

### 1.2 Non-goals (explicitly out of scope)

- Server-side rendering (SSR / Node canvas)
- Accessibility (ARIA roles, keyboard navigation, screen reader support)
- Plugins, theming, or animation APIs
- Bar, pie, scatter-matrix, or categorical chart types
- CommonJS output
- WebGL rendering back-end
- OffscreenCanvas / Worker-based rendering
- Built-in data decimation (caller is responsible)

---

## 2. Architecture overview

```
┌──────────────────────────────────────────────────────────┐
│  ChartController (reactive shared state)                 │
│  xDomain · zoom · highlight · series registry            │
└────────────────┬─────────────────────────────────────────┘
                 │ signal (push, no init sync)
    ┌────────────▼──────────────────────────────────┐
    │  Chart (per-instance)                         │
    │                                               │
    │  ┌──────────────────────────────────────┐     │
    │  │  Viewport guard (IntersectionObserver)│     │
    │  │  Off-viewport → suspended             │     │
    │  └──────────────────────────────────────┘     │
    │                                               │
    │  DOM host (position:relative, overflow:hidden)│
    │  ├── <canvas> main      (z:0, rasterised path)│
    │  ├── <canvas> highlight (z:1, hover series)   │
    │  └── <div>   overlay   (z:2, axes/crosshair)  │
    │       ├── SVG or DOM axes + tick labels        │
    │       ├── <div> crosshair (CSS transform)      │
    │       └── <div> zoom-rect (pointer capture)    │
    └───────────────────────────────────────────────┘
```

### 2.1 Rendering philosophy

Two stacked canvases decouple expensive path work from cheap hover effects:

- **Main canvas** — full series paths, band fills; invalidated only on data/zoom/resize change.
- **Highlight canvas** — re-drawn on every pointer move; draws one highlighted series and the
  crosshair dot. Cleared with a single `clearRect`.
- **Overlay div** — axes, tick labels, crosshair line, zoom-rect box; pure CSS/DOM, zero canvas
  cost.

This avoids compositing an entire frame when only hover state changes.

---

## 3. Coordinate systems and transforms

### 3.1 Data space → canvas space pipeline

```
data (x, y)
  │  scale transform (linear / log / symlog)
  ▼
normalized (nx ∈ [0,1], ny ∈ [0,1])  ← Path2D cache lives here
  │  viewport transform (pan + zoom)
  ▼
view-normalized (vx ∈ [0,1], vy ∈ [0,1])
  │  pixel transform (multiply by CSS width × DPR, height × DPR)
  ▼
device pixels (canvas coordinates)
```

### 3.2 Path2D caching in zoom-normalized coordinates

Path2D objects are cached at **normalized coordinates** (post-scale, pre-zoom). On zoom change only
the canvas `setTransform` is updated; cached Path2D objects are reused without recomputation unless
the underlying data or scale changes.

Cache key: `seriesId + scaleType + scaleParams`

Invalidation triggers:

- Data array reference changes (detected by identity, not deep equality)
- Scale type or computed params change
- Chart pixel dimensions change by more than 1 px (raster-cap rounding)

### 3.3 Raster-cap and DPR handling

```
devicePixelRatio = Math.min(window.devicePixelRatio, MAX_DPR)
MAX_DPR = 2   // cap; retina enough, avoids 3× GPU memory on HiDPI phones
```

Canvas physical size: `cssWidth × dpr` × `cssHeight × dpr`.  
ResizeObserver fires on CSS size change; canvas is resized and all Path2D caches for that chart are
invalidated.

---

## 4. Scale system

### 4.1 Linear scale

Standard affine mapping. No special cases.

### 4.2 Log scale — implemented as symlog with auto-derived params

Pure log axes break at zero and produce misleading compression for values near zero. **All log-mode
axes use symlog**, making log a strict special case of symlog.

#### Symlog definition

```
symlog(x, C) =
  sign(x) × log10(1 + |x| / C)
```

`C` is the **linear threshold** — the boundary below which the scale is approximately linear.

#### Auto-derivation of C

The library derives `C` automatically from the data visible in the current view:

```
nonzero = data.filter(v => isFinite(v) && v !== 0)
absMin  = min(|nonzero|)   // smallest absolute non-zero value
absMax  = max(|nonzero|)

// C = geometric mean of range boundaries, clamped to [1e-9, 1]
C = clamp(sqrt(absMin × absMax) / 100, 1e-9, 1)
```

`C` is re-derived whenever the visible x-domain changes or data updates. A stable `C` is not
guaranteed across zoom levels; callers requiring reproducible axis labels should pin `C` via the
`symlogThreshold` prop.

#### Inverse (for tick placement)

```
symlogInv(y, C) = sign(y) × C × (10^|y| − 1)
```

Ticks are placed in symlog space at regular intervals, then back-projected.

### 4.3 Scale configuration API

```ts
type ScaleConfig =
  | { type: "linear" }
  | { type: "log" } // sugar → symlog, C auto-derived
  | { type: "symlog"; threshold?: number }; // explicit C, or auto if omitted
```

---

## 5. Data model

### 5.1 Series definition

```ts
interface SeriesDef {
  id: string; // stable, used as Path2D cache key
  label?: string;
  xValues: Float64Array; // monotone, pre-sorted; may be independent per series
  yValues: Float64Array; // parallel; NaN = gap; Infinity = +Inf marker; -Infinity = -Inf marker
  color: string; // CSS color string, resolved once at render time
  width?: number; // stroke width in CSS px, default 1.5
  type: "line" | "point" | "band";
  // band only:
  yLow?: Float64Array; // lower bound; yValues is upper bound
  // point only:
  pointRadius?: number; // CSS px, default 3
}
```

### 5.2 Data normalization

Before rendering, the library normalizes incoming arrays into internal form:

1. **Type coercion** — accepts `number[]`, `Float32Array`, or `Float64Array`; always stored
   internally as `Float64Array`.
2. **NaN / ±Inf scan** — a single linear pass tags indices with special values; separate arrays
   `nanMask`, `posInfMask`, `negInfMask` are computed once per series update.
3. **Extent computation** — finite min/max for scale derivation, ignoring NaN/Inf.
4. **Monotonicity assertion** — `xValues` must be non-decreasing; violated in dev mode throws, in
   production silently clips.

Normalization is triggered only when the `id`-keyed data reference changes.

### 5.3 Special value rendering

| Value       | Visual                                                                    |
| ----------- | ------------------------------------------------------------------------- |
| `NaN`       | Path break (moveTo next finite point); small diamond marker at gap edges  |
| `+Infinity` | Upward-pointing triangle at the x position, clipped to top axis edge      |
| `-Infinity` | Downward-pointing triangle at the x position, clipped to bottom axis edge |

Markers are drawn on the **highlight canvas** when the series is active, on the **main canvas** at
reduced opacity otherwise.

---

## 6. Chart controller

### 6.1 Reactive shared state

The `ChartController` manages shared state across charts. It is **reactive-only**: state changes are
pushed to subscribers; there is no synchronous initialization broadcast.

**Motivation:** synchronous initialization causes blink storms when 100+ charts mount nearly
simultaneously. Each chart renders from its own initial state on first paint; the controller's state
is applied only after the chart has mounted and subscribed.

```ts
class ChartController {
  // Writable signals
  xDomain: Signal<[number, number]>;
  zoom: Signal<ZoomState>; // { xMin, xMax, yMin?, yMax? }
  highlight: Signal<HighlightState>; // { seriesId, xValue, yValue }

  // Methods
  subscribe(chart: ChartInstance): Unsubscribe;
  setXDomain(domain: [number, number]): void;
  zoomTo(zoom: ZoomState): void;
  resetZoom(): void;
  setHighlight(h: HighlightState | null): void;
}
```

### 6.2 Signal semantics

Signals are **push-based**, not pull-based. Subscribers receive the new value; they do not poll.

Signals batch updates within a microtask: multiple synchronous writes to `xDomain` and `zoom` within
the same call stack produce exactly one subscriber notification.

### 6.3 Controller ↔ chart lifecycle

```
chart.mount()
  → registers with controller (if provided)
  → controller pushes current state on next microtask (NOT synchronously)
  → chart renders from props-initial state first
  → controller update arrives → chart re-renders if state differs

chart.unmount()
  → unregisters from controller
  → controller retains no reference to the chart
```

---

## 7. Virtualization

### 7.1 Off-viewport suspension

Each chart instance holds an `IntersectionObserver`. When the chart's root element leaves the
viewport (intersection ratio = 0), the chart enters **suspended** state:

- Main canvas: frozen (no repaints).
- Highlight canvas: cleared, no pointer event processing.
- Controller subscription: paused (state queued, not applied).

On re-entry, queued controller state is applied in a single repaint. The chart does not paint
intermediate states.

### 7.2 Thresholds

```ts
const INTERSECTION_THRESHOLD = 0; // any pixel visible = active
const SUSPENSION_MARGIN = "200px"; // rootMargin; wake up slightly before visible
```

The suspension margin ensures charts begin their first paint slightly before scrolling into view,
eliminating pop-in.

---

## 8. Zoom interaction

### 8.1 Zoom modes

| Mode         | Gesture                        |
| ------------ | ------------------------------ |
| X-axis zoom  | Drag on plot area (left/right) |
| Reset        | Double-click or Escape         |
| Programmatic | `controller.zoomTo(...)`       |

Y-axis zoom is not supported via gesture (ML loss curves benefit from fixed y-axis during x-zoom).
Y-axis can be set programmatically.

### 8.2 Zoom-rect implementation

The zoom-rect `<div>` sits in the overlay layer with `pointer-events: all`. It captures
`pointerdown`, `pointermove`, `pointerup` using the Pointer Events API.

- On drag: CSS `width` / `left` of the zoom-rect `<div>` is updated directly (no canvas repaint).
- On release: `controller.zoomTo` is called with the new x domain; all subscribed charts update.

### 8.3 Path2D reuse on zoom

After zoom, the canvas `setTransform` is updated to map the new [xMin, xMax] to canvas width. Cached
Path2D objects drawn at normalized coordinates are rendered through the new transform without
recomputation.

This makes zoom on 100 k-point series essentially free — only transform math, no path rebuild.

---

## 9. Axes and tick generation

Axes are rendered in the DOM overlay, not on canvas. This avoids canvas text rendering cost and
enables CSS font smoothing.

### 9.1 Tick algorithm

```
targetTickCount = floor(axisPxLength / MIN_TICK_PX_SPACING)
MIN_TICK_PX_SPACING = 60   // px between ticks

// For linear axes: standard "nice" algorithm (d3-like, no d3 dependency)
// For symlog axes: ticks placed at symlog-space regular intervals, back-projected
```

Ticks are recalculated only when the domain or pixel dimensions change.

### 9.2 Tick label formatting

| Value range                  | Format                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| Integer, < 1 M               | `1,234` (locale-grouped)                                                            |
| Float                        | Up to 4 significant digits, no trailing zeros                                       |
| Large (≥ 1 M)                | SI suffix: `1.2M`, `3.4B`                                                           |
| Scientific                   | `1.23e+10` for very large/small when SI would lose precision                        |
| Time (if xValues is Unix ms) | Detected automatically; formatted as `HH:mm:ss` or `MM-DD` depending on domain span |

---

## 10. Crosshair

The crosshair is a full-height vertical `<div>` in the overlay, positioned via
`transform: translateX(...)`. Position is updated on `pointermove` over the overlay div.

On pointer move:

1. Convert pointer x to data-space x via inverse viewport transform.
2. Binary-search each series' `xValues` for nearest x (O(log n) per series).
3. Write `controller.setHighlight(...)` — all subscribed charts update crosshair position.
4. Draw highlight series path segment on the highlight canvas.

Crosshair DOM update and highlight canvas repaint are batched in a single `requestAnimationFrame`.

---

## 11. Rendering pipeline (per frame)

```
Invalidation trigger (data / zoom / resize)
  │
  ▼
1. Compute scale params (extent, C for symlog)
2. Compute viewport transform (zoom → canvas transform matrix)
3. For each series (in z-order):
   a. Lookup Path2D from cache by (seriesId, scaleType, scaleParams)
   b. If cache miss → buildPath2D(series, scale) → store
   c. ctx.save(); ctx.setTransform(viewportMatrix); ctx.stroke(path2D); ctx.restore()
4. Draw band fills (if any) — separate cached Path2D per band
5. Draw NaN/±Inf markers (from pre-computed masks)
6. Update axis tick DOM nodes
7. Done

Highlight frame (pointer move only):
  1. clearRect highlight canvas
  2. Redraw active series path with increased strokeWidth
  3. Draw crosshair dot
  4. Update crosshair div translateX
```

---

## 12. Independent X per series

Series within a single chart may have different `xValues` arrays. The chart maintains one shared
x-axis domain (the union of all series x-extents), but each series is transformed using its own
`xValues`.

The viewport transform is parameterized by the shared x-domain; each series' path is built using a
per-series x-to-normalized mapping before the shared zoom transform is applied.

```
series.xToNorm(x) = (x - seriesXMin) / (seriesXMax - seriesXMin)
// then: sharedViewport.normToCanvas(nx)
```

This enables plotting a 1-Hz series alongside a 1-kHz series on the same time axis.

---

## 13. Performance constraints and budget

| Budget                                  | Constraint                            |
| --------------------------------------- | ------------------------------------- |
| First paint (100 k pts)                 | ≤ 16 ms                               |
| Zoom repaint (100 k pts, cached Path2D) | ≤ 2 ms                                |
| Pointer move → crosshair update         | ≤ 1 frame (16.7 ms)                   |
| 100 charts, idle                        | 0 repaints (no animation loop)        |
| Memory per series (100 k pts)           | ≤ 3.2 MB (`Float64Array` × 2 + masks) |

### 13.1 No animation loop

The library does **not** run a continuous `requestAnimationFrame` loop. Repaints are scheduled only
on explicit invalidation (data change, zoom, resize, pointer move). Idle dashboards consume zero
CPU.

### 13.2 Path2D size limits

A `Path2D` with 100 k line segments is ~3–5 MB of GPU command buffer. The library does not split
paths. Browser implementations (Chrome, Firefox, Safari) handle 100 k-command Path2D objects without
issue; this is a known-acceptable size.

At 1 M points, Path2D size would exceed practical limits; the library emits a console warning if a
series exceeds 200 k points and rendering is attempted without pre-aggregation.

---

## 14. React integration

The React layer is a **peer integration**, not a core dependency. It lives in a separate entry
point: `velox-plot/react`.

```ts
// Core (zero deps)
import { Chart, ChartController } from "velox-plot";

// React peer layer
import { VeloxChart, useChartController } from "velox-plot/react";
```

### 14.1 Hooks

```ts
function useChartController(initial?: ControllerInit): ChartController;
```

Returns a stable `ChartController` instance. Controller state changes trigger React renders only for
components that have explicitly subscribed to a specific signal.

### 14.2 VeloxChart component

```tsx
<VeloxChart
  series={series}        // SeriesDef[]
  controller={ctrl}      // optional; omit for standalone chart
  xScale={xScaleConfig}  // ScaleConfig
  yScale={yScaleConfig}  // ScaleConfig
  height={300}           // CSS px
  style={...}            // forwarded to host div
/>
```

The component mounts a core `Chart` instance into a `<div>` ref. All prop changes are diffed and
forwarded to the imperative `Chart` API; no React re-renders trigger canvas repaints unless data or
config actually changes.

---

## 15. Public API surface (core)

```ts
// Controller
class ChartController { ... }   // see §6

// Chart
class Chart {
  constructor(el: HTMLElement, opts: ChartOptions)
  setSeries(series: SeriesDef[]): void
  setXScale(cfg: ScaleConfig): void
  setYScale(cfg: ScaleConfig): void
  setController(ctrl: ChartController | null): void
  destroy(): void
}

interface ChartOptions {
  series?: SeriesDef[]
  xScale?: ScaleConfig
  yScale?: ScaleConfig
  controller?: ChartController
  height?: number
}

// Scales
type ScaleConfig =
  | { type: 'linear' }
  | { type: 'log' }
  | { type: 'symlog'; threshold?: number }

// Series
interface SeriesDef { ... }   // see §5.1
```

---

## 16. Module structure

```
src/
  core/
    chart.ts          // Chart class, canvas management
    controller.ts     // ChartController, Signal
    path-cache.ts     // Path2D cache keyed by seriesId+scale
    scales.ts         // linear, symlog transforms + tick gen
    normalize.ts      // data normalization, NaN/Inf masks
    render.ts         // main + highlight canvas render pipeline
    axes.ts           // DOM tick/label management
    crosshair.ts      // pointer events, highlight dispatch
    zoom.ts           // zoom-rect interaction
    viewport.ts       // DPR, ResizeObserver, IntersectionObserver
    constants.ts      // MAX_DPR, thresholds, defaults
  react/
    VeloxChart.tsx
    useChartController.ts
  index.ts            // re-exports core
  react.ts            // re-exports react layer

dist/
  velox-plot.js       // ESM
  velox-plot/react.js // ESM React peer layer
  velox-plot.d.ts
```

---

## 17. Rejected approaches and rationale

### 17.1 WebGL

Rejected. Browsers enforce a **16-context limit** across all canvases on a page; 100+ charts would
silently degrade to software rendering or lose contexts. WebGL also lacks native wide-line and
dashed-stroke primitives, requiring custom geometry shaders that add complexity without proportional
benefit at 100 k-point scale. Canvas2D Path2D at this scale is fast enough.

### 17.2 OffscreenCanvas + Workers

Rejected. Transferring path data or bitmap results across the Worker/main-thread boundary via
`postMessage` introduces **IPC serialization cost** that erases the parallelism benefit for 100
k-point paths. Synchronizing 100+ workers with a shared controller adds coordination overhead. The
zoom-transform optimization (§8.3) makes main-thread rendering cheap enough that off-thread
rendering is unnecessary.

### 17.3 Decimation

Rejected as a built-in feature. The library targets pre-aggregated data (server-side LTTB or min-max
envelope). Built-in decimation would add complexity, produce inconsistent results across zoom
levels, and mask outliers — the primary use case for ML dashboards.

---

## 18. Open questions

| #   | Question                                                                    | Default assumption                                         |
| --- | --------------------------------------------------------------------------- | ---------------------------------------------------------- |
| 1   | Should `ChartController` support y-domain sync across charts?               | No; y-axes are independent                                 |
| 2   | Should band charts support per-pixel opacity (alpha gradient)?              | No; flat fill with configurable alpha                      |
| 3   | Should `SeriesDef.xValues` be optional (implicit integer index)?            | No; always explicit                                        |
| 4   | Should the React layer support `ref` forwarding to `Chart` instance?        | Yes                                                        |
| 5   | Is a `pinC` (pinned symlog threshold) needed per-chart or per-series?       | Per-axis (per-chart)                                       |
| 6   | Should ±Inf markers render on the main or highlight canvas when not active? | Main canvas, reduced opacity                               |
| 7   | Min browser target?                                                         | Chrome 100, Firefox 100, Safari 16 (no IE, no legacy Edge) |
