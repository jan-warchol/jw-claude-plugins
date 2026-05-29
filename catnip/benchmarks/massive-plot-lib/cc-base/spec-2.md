# PlotLib — Technical Specification

**Version:** 0.1.0-draft  
**Date:** 2026-05-29  
**Status:** Draft

---

## 1. Purpose and Scope

PlotLib is a zero-dependency, ESM-only, canvas-based charting library for ML training dashboards. It
renders line, point, and band (area-between-two-series) charts at interactive frame rates with up to
100 000 rendered points per chart and up to 100+ charts simultaneously visible in a single browser
tab.

### Performance Targets

| Metric                      | Target                        |
| --------------------------- | ----------------------------- |
| Initial render (100k pts)   | < 16 ms (one frame at 60 fps) |
| Pan/zoom re-render          | < 8 ms                        |
| Crosshair move              | < 2 ms                        |
| 100 charts cold load        | < 500 ms total                |
| Memory per chart (100k pts) | < 8 MB heap                   |

These targets match or exceed uPlot on throughput and Dygraphs on interaction responsiveness.

### Out of Scope (Permanently)

- SSR / Node rendering
- Accessibility (ARIA, keyboard navigation, screen-reader hooks)
- Plugins, theming, animations, transitions
- Bar, pie, and categorical chart types
- CommonJS output; ESM only
- WebGL (browser 16-context limit; no native wide lines or dashes)
- OffscreenCanvas / Web Workers (IPC serialization cost exceeds rendering cost at this scale)

---

## 2. Data Model

### 2.1 Series

```ts
interface Series {
  id: string; // stable, used as cache key
  label: string;
  x: Float64Array; // monotonically non-decreasing; independent per series
  y: Float64Array; // same length as x; NaN / ±Infinity allowed
  color: string; // CSS color string
  width?: number; // stroke width, default 1.5 px
  type: "line" | "point" | "band-lower" | "band-upper";
  bandPairId?: string; // links a band-lower to its band-upper by series id
  yAxis?: "left" | "right";
}
```

**Rules:**

- `x` and `y` must be `Float64Array`; the library rejects plain `number[]` at the type level
  (TypeScript overload) but coerces at runtime with a one-time copy and a `console.warn`.
- `x` values must be finite and non-decreasing; violations are clamped silently in release builds
  and throw in development (`NODE_ENV !== "production"`).
- `NaN` in `y` breaks the path (gap). `+Infinity` and `-Infinity` are rendered as clipped markers
  (see §6.4).
- A series `id` must remain stable across re-renders; it is the key into the Path2D cache (§7).

### 2.2 Chart Config

```ts
interface ChartConfig {
  id: string;
  series: Series[];
  title?: string;
  xLabel?: string;
  yLeftLabel?: string;
  yRightLabel?: string;
  xScale?: ScaleConfig;
  yLeftScale?: ScaleConfig;
  yRightScale?: ScaleConfig;
}

interface ScaleConfig {
  type: "linear" | "log" | "symlog";
  min?: number; // override auto-fit
  max?: number;
  // symlog: if omitted, linthresh is auto-derived (see §5.3)
  linthresh?: number;
  linscale?: number;
}
```

### 2.3 View State

View state is managed by the shared `PlotController` and never stored inside chart components.

```ts
interface ViewState {
  xMin: number;
  xMax: number;
  // yMin/yMax are per-chart, derived from visible data; not stored here
  highlightX: number | null; // crosshair position in data coords
  zoomRect: ZoomRect | null;
}

interface ZoomRect {
  x0: number;
  x1: number;
  y0: number;
  y1: number; // in data-space
  chartId: string; // which chart initiated the drag
}
```

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  React tree                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  <PlotProvider controller={ctrl}>                │   │
│  │    <VirtualList>                                 │   │
│  │      <Chart id="c1" />   ← off-viewport: skip   │   │
│  │      <Chart id="c2" />   ← visible: render      │   │
│  │      ...                                         │   │
│  │    </VirtualList>                                │   │
│  │  </PlotProvider>                                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

Per visible <Chart>:
┌──────────────────────────────────────────────────────────┐
│  div.chart-root  (position: relative)                    │
│  ├── canvas.main          z-index 0  (series paths)      │
│  ├── canvas.highlight     z-index 1  (hover emphasis)    │
│  └── div.overlay          z-index 2  (axes, labels,      │
│                                       crosshair line,    │
│                                       zoom-rect DOM el)  │
└──────────────────────────────────────────────────────────┘
```

Three layers per chart:

1. **`canvas.main`** — redrawn only on zoom/pan/data change. Holds all series paths. Expensive;
   cached.
2. **`canvas.highlight`** — redrawn on every pointer move. Holds the highlighted nearest-point
   marker and optional series emphasis (brightness/opacity shift). Cheap; small.
3. **`div.overlay`** — plain DOM. Axes are SVG-less CSS (`border`, `transform`). Crosshair is a
   `div` with `transform: translateX`. Zoom-rect is a `div` with absolute positioning. Text (tick
   labels, axis labels) is `<span>`. Zero canvas text; zero SVG.

---

## 4. PlotController

### 4.1 Construction

```ts
const ctrl = new PlotController(initialViewState?: Partial<ViewState>);
```

The controller is a plain class, not a React object. It holds a `Map<string, Set<Listener>>` per
event type and uses `requestAnimationFrame` coalescing for batch updates.

### 4.2 Reactive-Only Synchronization

**Rule:** The controller never pushes state synchronously at initialization. Charts subscribe on
mount and receive state on the next RAF tick. This eliminates "async blink storms" — the condition
where 100 charts each trigger a synchronous render chain during mount, causing visible cascaded
repaints.

Implementation:

```ts
class PlotController {
  private pending = false;
  private state: ViewState = defaultViewState();

  update(patch: Partial<ViewState>) {
    Object.assign(this.state, patch);
    if (!this.pending) {
      this.pending = true;
      requestAnimationFrame(() => {
        this.pending = false;
        this.emit("change", this.state);
      });
    }
  }
}
```

All chart components call `ctrl.subscribe("change", cb)` on mount and unsubscribe on unmount. First
paint uses the state available at commit time (from React context snapshot), so the initial render
is correct without waiting for the RAF tick.

### 4.3 Shared Highlight

`highlightX` is broadcast in data-space coordinates (not pixel). Each chart independently maps this
to its own pixel space. A chart with no data near `highlightX` renders nothing on the highlight
layer.

### 4.4 Zoom

Zoom interactions on any chart update `ctrl.state.xMin / xMax`, which all charts receive via the RAF
batch. Y-axis zoom is chart-local (not broadcast) to support independent Y scales across charts.

---

## 5. Scale System

### 5.1 Linear

Standard linear mapping. Min/max auto-fit to visible data extent with 5 % padding.

### 5.2 Log

Log scale is implemented as a special case of symlog with `linthresh` = 0 (i.e., the linear region
has zero width). Charts requesting `type: "log"` are internally rewritten to `type: "symlog"` with
`linthresh` auto-derived. Callers never need to know the difference.

The public API exposes `"log"` as a convenience alias. Internally there is one code path.

### 5.3 Symlog

Symlog maps:

```
symlog(x) =
  sign(x) * log(1 + |x| / linthresh) * linscale   if |x| >= linthresh
  x / linthresh * linscale                          if |x| < linthresh
```

**Auto-derivation of `linthresh`:** when not provided, scan the visible Y data for the smallest
nonzero absolute value `v_min` and the largest `v_max`. Set:

```
linthresh = v_min * 10^(0.5 * log10(v_max / v_min))
```

This places the linear/log transition at the geometric midpoint of the nonzero data range,
minimizing visual distortion. Recomputed on zoom if the visible set changes.

`linscale` defaults to `1.0` (the matplotlib default).

### 5.4 Tick Generation

Ticks are generated in scale-space, not pixel-space. For symlog, ticks are placed at powers of 10 in
the log regions and linearly in the linear region. Tick density targets ~5–8 ticks on the primary
axis, ~4–6 on secondary.

---

## 6. Rendering Pipeline

### 6.1 Data Normalization Pass

On series assignment (not on every render), run once:

1. Validate `x` monotonicity (dev mode only beyond 1k points, sampled).
2. Build a sorted index if `x` is shared across series (common for training steps).
3. Identify NaN runs and ±Inf indices; store as `Float32Array` index lists on the series metadata
   object.

This pass is O(n) and amortized over all subsequent renders.

### 6.2 Viewport Clipping

Before path construction, binary-search `x` array for `[xMin, xMax]` to find `[iStart, iEnd]`.
Render only points in this slice. This is the primary mechanism for 1M-point usability: a 1M-point
series with a 1000x zoom shows ~1000 points and renders in the same time as a 1000-point series.

Binary search uses the native `Float64Array` layout for cache efficiency. No library needed.

### 6.3 Path Construction

```ts
function buildPath(
  series: NormalizedSeries,
  iStart: number,
  iEnd: number,
  toPixelX: (x: number) => number,
  toPixelY: (y: number) => number,
): Path2D;
```

- `moveTo` on first valid point; `lineTo` for subsequent valid points.
- On `NaN`: `moveTo` next valid point (gap).
- On `±Infinity`: skip from path; record pixel X in a separate array for marker rendering (§6.4).
- `point` type: skip path construction; render circles in a separate pass using `arc()` calls
  batched into one `Path2D`.
- `band` type: build upper path forward, lower path backward, close — one filled `Path2D`.

Path construction is the hot loop. Keep it branch-minimal:

```ts
let penDown = false;
for (let i = iStart; i <= iEnd; i++) {
  const yv = y[i];
  if (yv !== yv) {
    penDown = false;
    continue;
  } // NaN fast path
  const px = toPixelX(x[i]);
  const py = toPixelY(yv);
  penDown ? path.lineTo(px, py) : (path.moveTo(px, py), (penDown = true));
}
```

`yv !== yv` is the fastest NaN check; no `isNaN` call.

### 6.4 NaN/±Infinity Markers

- **NaN gap:** rendered implicitly by the path break. No additional marker.
- **+Infinity:** small upward-pointing triangle clipped to the top axis edge at the correct X.
- **-Infinity:** small downward-pointing triangle clipped to the bottom axis edge.
- Markers are drawn after the main stroke pass on the same `canvas.main`.
- Batched into a single `Path2D` per marker type per series.

### 6.5 Rendering Order

On `canvas.main` (full repaint only):

1. Clear canvas.
2. For each `band` pair: fill band `Path2D` at low alpha (0.15).
3. For each `line` series: stroke `Path2D`.
4. For each `point` series: fill point `Path2D`.
5. For each series with ±Inf markers: stroke marker `Path2D`.

On `canvas.highlight` (pointer-move repaint):

1. Clear canvas.
2. Find nearest point to `highlightX` via binary search in visible slice.
3. Draw one filled circle at nearest point per series (skip if delta > threshold).
4. Optionally: reduce opacity of non-nearest series (draw dim rect over main canvas is too
   expensive; instead skip and only mark nearest).

### 6.6 DPR and Raster Cap

```ts
const DPR = Math.min(window.devicePixelRatio, 2);
```

Cap at 2× regardless of actual DPR (e.g., 3× on some phones). Beyond 2×, the rendering cost grows
faster than the perceptual benefit for dense line charts.

Canvas physical size = CSS size × DPR. All Path2D construction uses physical pixels. The
`ctx.scale(DPR, DPR)` call is made once after resize; paths are built in physical pixels directly
rather than relying on the transform (avoids a matrix multiply per point).

`ResizeObserver` watches the chart root div. On resize:

1. Recompute canvas physical dimensions.
2. Invalidate all Path2D cache entries for this chart (zoom-normalized coords are pixel-dependent —
   see §7).
3. Schedule full repaint on next RAF.

---

## 7. Path2D Cache

### 7.1 Cache Key

```
key = `${series.id}:${xMin.toPrecision(6)}:${xMax.toPrecision(6)}:${canvasWidth}:${canvasHeight}`
```

- `series.id` stability is a contract with the caller (documented, not enforced).
- `toPrecision(6)` quantizes float keys to avoid cache misses from floating-point noise in repeated
  pan/zoom interactions.
- `canvasWidth` and `canvasHeight` are physical pixel dimensions.

### 7.2 Cache Structure

```ts
const pathCache = new Map<string, Path2D>();
const MAX_CACHE_ENTRIES = 512;
```

LRU eviction: maintain an insertion-order doubly linked list alongside the map. On get: promote to
head. On insert beyond max: evict tail.

### 7.3 Cache Invalidation

| Event                       | Invalidation scope            |
| --------------------------- | ----------------------------- |
| Data update for series `id` | All entries with prefix `id:` |
| Resize                      | All entries for this chart    |
| Scale type change           | All entries for this chart    |
| Data update + no id change  | All entries for this chart    |

### 7.4 Zoom-Normalized Coordinates

Paths are built in pixel coordinates for the current viewport. This is simpler and faster than
building in data-space and applying a CSS transform, which would require subpixel correction on
every zoom level and complicates the NaN marker clipping logic.

Trade-off: cache miss on every new zoom level. Mitigated by the quantized key (§7.1) snapping nearby
zoom levels to the same bucket.

---

## 8. Axis and Overlay System

Axes are rendered in DOM, not canvas. Rationale: text rendering in canvas requires measuring, font
loading, and manual wrapping; DOM text is free and accessible to the browser's layout engine.

### 8.1 X Axis

```
div.x-axis
  ├── div.tick  style="left: {px}px" × N
  │     └── span.tick-label "{formatted value}"
  └── div.axis-line
```

Tick positions are computed in JS and applied as `style.left` via `element.style.left = px + "px"`.
No `transform`; `left` is cheaper for many absolutely-positioned children.

### 8.2 Y Axis

```
div.y-axis-left
  └── div.tick  style="top: {px}px" × N
        └── span.tick-label "{formatted value}"
```

Tick labels on Y are right-aligned for the left axis, left-aligned for the right axis.

### 8.3 Crosshair

```
div.crosshair-x  style="transform: translateX({px}px)"
div.crosshair-y  style="transform: translateY({px}px)"  // optional
```

`translateX` uses GPU-composited transforms; no layout thrash. Updated on `pointermove` inside a RAF
gate (one DOM write per frame max).

### 8.4 Zoom Rect

On `pointerdown` + drag, a `div.zoom-rect` is positioned with `left/top/width/height`. On
`pointerup`, `ctrl.update({ xMin, xMax })` is called and the div is hidden.

The zoom rect is drawn in DOM (not canvas) so it does not trigger a canvas repaint during drag.

---

## 9. Viewport Virtualization

### 9.1 Mechanism

`<VirtualList>` uses a single `IntersectionObserver` with `rootMargin: "200px"`. Charts outside this
margin are unmounted and replaced with a placeholder `div` of the same height (height is stored in a
`Map<chartId, number>` on the controller to preserve scroll position).

Charts within the margin are mounted and rendered normally.

### 9.2 Off-Viewport Path Cache

Path2D objects are owned by the chart component. When a chart unmounts (leaves viewport), its Path2D
cache is also garbage-collected. On re-entry, paths are rebuilt. This is acceptable because re-entry
rebuilds take < 16 ms for 100k points (§1 performance target).

For persistent caching across remounts, the caller can optionally hold a `PathCacheRef` (an opaque
object returned by `usePlotCache(chartId)`) in component state outside the virtual list. This is
opt-in; the default is no cross-mount persistence.

### 9.3 Height Estimation

Before a chart has ever been mounted, height defaults to `300px` (configurable via
`<VirtualList defaultItemHeight={n}>`). After first mount, the measured height is stored. Scroll
position jitter on rapid scroll is bounded to ±(measured − estimated) pixels per unmounted chart.

---

## 10. React Integration

### 10.1 Provider

```tsx
<PlotProvider controller={ctrl}>{children}</PlotProvider>
```

Provides the `PlotController` via React context. Does not subscribe to controller events itself;
each `<Chart>` subscribes independently.

### 10.2 Chart Component

```tsx
<Chart
  config={chartConfig}       // ChartConfig
  height={300}               // px, default 300
  className?: string
/>
```

Internal hooks:

- `useLayoutEffect` for canvas sizing (must run before paint).
- `useEffect` for controller subscription.
- `useRef` for canvas elements, Path2D cache, and render state.
- No `useState` for render-triggering — all repaints are imperative (`canvas.getContext("2d")...`)
  to avoid React reconciliation overhead during animation.

**Critical:** chart components call `ctx.clearRect` and draw imperatively; they do not re-render the
React tree on zoom/pan. React renders only on:

1. `config` prop reference change (new series or config object).
2. Initial mount.
3. Resize (canvas dimension update requires a React re-render to set `canvas.width/height`).

### 10.3 usePlotController Hook

```ts
const ctrl = usePlotController();
// returns the nearest PlotProvider's controller, throws if none
```

### 10.4 Peer Dependency

```json
"peerDependencies": {
  "react": ">=18.0.0",
  "react-dom": ">=18.0.0"
}
```

No bundled React. No `react` import in non-React code paths (scale, path, cache modules have no
React dependency).

---

## 11. Independent X Per Series

Each `Series` carries its own `x: Float64Array`. When a chart has series with different X arrays:

- Crosshair nearest-point lookup is done independently per series (binary search each `x` array).
- The X axis tick range spans `min(all series xMin)` to `max(all series xMax)` for the visible
  window.
- `toPixelX` is shared (same X scale for all series in a chart); the X arrays may differ in sample
  density or domain.
- A series whose `x` range does not overlap the current viewport is not rendered (no points
  visible).

This supports the common ML case of comparing runs with different step counts or timestamp offsets
on the same chart without requiring the caller to align or interpolate.

---

## 12. Module Structure

```
src/
  index.ts              — public API re-exports
  controller.ts         — PlotController, ViewState
  scale.ts              — linear, symlog (log alias)
  normalize.ts          — data normalization, NaN/Inf indexing
  path.ts               — Path2D construction, point/line/band
  render.ts             — canvas paint orchestration
  axes.ts               — tick generation, DOM axis helpers
  cache.ts              — LRU Path2D cache
  react/
    PlotProvider.tsx
    Chart.tsx
    VirtualList.tsx
    hooks.ts
  types.ts              — Series, ChartConfig, ScaleConfig, ViewState
```

No circular dependencies. `react/` imports from `../controller`, `../types`; never from `../render`
directly (render is called imperatively from Chart.tsx).

### Build Output

```
dist/
  index.js        — ESM, unbundled (imports preserved)
  index.d.ts
  react.js        — ESM, React components only
  react.d.ts
```

Bundler (Rollup or esbuild) produces two entry points. Tree-shaking eliminates React code when only
the core (scale, controller, path) is imported.

---

## 13. Interaction Specification

### 13.1 Zoom

| Input              | Action                                               |
| ------------------ | ---------------------------------------------------- |
| Scroll wheel       | Zoom X axis centered on cursor; factor 1.15 per tick |
| Drag (left button) | Draw zoom rect; on release zoom to rect X range      |
| Double-click       | Reset to full data extent                            |
| Pinch (touch)      | Zoom X axis                                          |

Y-axis zoom is not triggered by default (too disorienting across 100+ charts). Y is always auto-fit
to visible X range unless `yLeft.min` / `yLeft.max` are pinned in config.

### 13.2 Pan

| Input                       | Action |
| --------------------------- | ------ |
| Drag on axis                | Pan X  |
| Drag on plot (no zoom mode) | Pan X  |

### 13.3 Highlight Sync

Pointer entering any chart sets `ctrl.highlightX` (broadcast to all charts). Pointer leaving all
charts (tracked with a shared `pointerleave` counter on the provider) clears it.

### 13.4 Interaction Modes

```ts
type InteractionMode = "zoom" | "pan" | "none";
```

Default: `"zoom"`. Settable per `<Chart>` or globally on the controller. `"none"` disables pointer
events on the canvas layers (the overlay div gets `pointer-events: none`), useful for read-only
dashboard tiles.

---

## 14. Number Formatting

All number formatting is done with `Intl.NumberFormat` (cached instances per locale+options).

- Axis tick labels: compact notation (`"1.2M"`, `"3.5k"`) for values ≥ 10 000 or ≤ 0.001.
- Crosshair tooltip values: full precision with up to 6 significant figures.
- Log/symlog axes: ticks formatted as powers of 10 where applicable (`10²`, `10⁻³`), using Unicode
  superscript or `<sup>` elements.

---

## 15. Error Handling

### Development Mode (`NODE_ENV !== "production"`)

- Throw on `x.length !== y.length`.
- Throw on non-monotonic `x` (checked on first 1000 points; beyond that, sampled at 1 %).
- Warn on missing `series.id`.
- Warn on `Float32Array` input (precision loss at >16M step counts).

### Production Mode

- Clamp and continue; no throws.
- `console.error` for fatal mismatches (length mismatch).

---

## 16. Testing Strategy

- **Unit:** scale functions (linear, symlog), tick generation, binary search viewport clipping,
  NaN/Inf detection.
- **Integration:** Path2D output shape given known inputs (mock canvas with path recording).
- **Visual regression:** Playwright screenshot tests for 5 canonical chart configs at fixed viewport
  sizes.
- **Performance benchmark:** scripted render loop (1000 render calls, 100k pts, record p50/p99 frame
  time). Fails CI if p99 > 20 ms.

---

## 17. Open Questions

1. **Tooltip DOM vs canvas:** current spec uses DOM for crosshair line but is silent on tooltip
   boxes. DOM tooltips are simpler but cause reflow if improperly positioned; canvas tooltips
   require text measuring. Decide before implementation.
2. **Right Y axis:** spec allows `yAxis: "right"` on series. Axis DOM layout with two Y axes plus
   the plot area requires careful CSS grid or absolute sizing. Define the pixel budget (axis width)
   as a constant or a prop.
3. **Path2D browser support:** `Path2D` is baseline-available (all evergreen browsers). Confirm the
   minimum target (drop IE11 explicitly in package.json `engines` / `browserslist`).
4. **`usePlotCache` API:** the opt-in cross-mount path cache ref (§9.2) is loosely defined. Specify
   the ref shape and whether it holds Path2D objects directly or only the cache map.
5. **Stable id enforcement:** the spec documents `series.id` stability as a contract. Consider a
   development-mode warning when an id disappears and reappears with different data (likely a bug in
   the caller).
