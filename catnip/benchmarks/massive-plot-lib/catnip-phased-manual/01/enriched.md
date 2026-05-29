# PlotLib — Canvas-Based High-Performance Plotting Library

## Purpose

A zero-dependency, ESM-only React library for rendering line, point, and band charts at massive
scale. Primary target: ML training dashboards where dozens to hundreds of charts are simultaneously
visible, each displaying pre-aggregated time-series data. The library must match uPlot's raw render
throughput and Dygraphs' interaction responsiveness without decimating data client-side.

---

## Scale Targets

| Dimension                   | Supported   | Notes                                            |
| --------------------------- | ----------- | ------------------------------------------------ |
| Points per chart            | ≤ 100k      | 100 series × 1 000 pts or 1 000 series × 100 pts |
| Points per chart (degraded) | ≤ 1 M       | Usable but not the design centre                 |
| Simultaneous visible charts | 100+        | Off-viewport charts are virtualized              |
| Series per chart            | Unbounded   | Performance scales with total point count        |
| Pre-aggregation             | Server-side | Client never decimates                           |

---

## Architecture

### Canvas Layer Stack

Each chart owns a fixed stack of two `<canvas>` elements and a DOM overlay, all absolutely
positioned and sized identically:

1. **Main canvas** — persistent series paths; redrawn only on zoom change or data update.
2. **Highlight canvas** — ephemeral per-frame content: hover series emphasis, active zoom rectangle,
   selected-point markers. Cleared and redrawn on every pointer event.
3. **DOM overlay** — axis ticks/labels, crosshair lines, zoom-rect border, tooltip anchor. Rendered
   via React so it participates in the normal layout system and is naturally accessible to CSS.

Separating main from highlight avoids full-chart redraws during mouse movement, which is the
dominant source of jank in naive implementations.

### Path2D Caching

All series paths are pre-compiled into `Path2D` objects in **zoom-normalized coordinates**: the
coordinate space is defined by the visible data window `[xMin, xMax] × [yMin, yMax]` mapped to
`[0, 1] × [0, 1]`. A `DOMMatrix` affine transform is applied at `ctx.stroke()` time to map the unit
square onto the physical canvas pixels.

Consequence: panning and zooming reuse cached paths by only changing the transform matrix — no path
recomputation. A cached path is invalidated only when the underlying data changes or when the series
is added/removed.

Cache keys are **stable series IDs** (strings, assigned by the caller), not array indices, so React
re-renders and chart reorderings do not bust the cache.

### Rendering Pipeline

```
data update or zoom change
  └─ for each visible chart
       ├─ resolve transform matrix from viewport ↔ data window mapping
       ├─ ctx.setTransform(matrix)
       ├─ ctx.clearRect(full canvas)
       └─ for each series
            ├─ if Path2D cache miss → compile path → cache
            └─ ctx.stroke(cachedPath)
```

Highlight redraws follow the same transform but skip caching entirely.

### Memory and Cache Eviction

Path2D objects accumulate as series are added across many charts. A global LRU eviction policy caps
the total cache at `MAX_CACHED_PATHS` entries (default: 2 000). When the cap is hit, the
least-recently-drawn paths are dropped first — these are typically off-viewport charts that have not
yet been virtualized (e.g., just left the viewport). Off-viewport charts whose
`IntersectionObserver` has fired are actively cleared; the LRU cap is a safety net for boundary
cases. Callers may override the cap via an optional `configure({ maxCachedPaths })` call.

### Virtualization

Charts outside the browser viewport are not rendered at all. An `IntersectionObserver` tracks each
chart root element. Off-viewport charts render only a transparent placeholder `<div>` of the correct
size (preserving layout and scroll position). Cached `Path2D` objects are retained so that
re-entering the viewport is instant.

### DPR / Resize Handling

A single shared `ResizeObserver` watches all chart containers. On resize (or device-pixel-ratio
change via `matchMedia`):

1. Canvas `width`/`height` attributes are updated to `layoutWidth × DPR` and `layoutHeight × DPR`.
2. A **raster cap** is applied: if the physical pixel count exceeds `MAX_CANVAS_PIXELS` (default: 16
   777 216, i.e. 4 096 × 4 096), DPR is clamped so the canvas stays within the cap.
3. All cached `Path2D` entries for the affected chart are invalidated (paths are in normalized
   coordinates, but stroke widths are device-pixel-absolute and must be recomputed).

### Rejected Rendering Backends

**WebGL** — Browser limit of 16 simultaneous WebGL contexts makes it incompatible with 100+ visible
charts. WebGL also lacks native support for variable-width lines and dashed strokes without complex
workarounds.

**OffscreenCanvas / Web Workers** — Transferring `ImageBitmap` results from a worker to the main
thread incurs serialization and IPC overhead that eliminates the theoretical benefit for the data
volumes targeted here. Synchronizing zoom/pan state across workers compounds this cost.

**SVG** — SVG DOM nodes scale poorly beyond a few thousand elements; 100k points as SVG path
segments degrades browser layout performance independently of rendering.

---

## Coordinate Systems

### X-Axis Model

Each series carries its own independent X array. The chart's visible X domain is the union of all
series' X ranges by default, or it can be set explicitly via the shared controller. Independent X
per series allows overlaying series sampled at different frequencies without interpolation or
alignment.

### Y-Domain Behavior

The Y domain is **per-chart and auto-derived**; it is not part of the shared controller. By default
the Y domain is computed from the y values of all series whose x range intersects the current
`xWindow` — i.e., it tracks the visible X window. This ensures outliers outside the zoomed region do
not compress the visible range. `ScaleConfig.min` / `ScaleConfig.max` override the auto-derived
bounds when set.

Y recalculation happens synchronously at the start of each main-canvas redraw (triggered by
`xWindow` changes). Because it only scans points within the current X window (via binary search on
sorted x), the cost scales with the visible point density, not the full series length.

### Scale Types

| Scale    | Description                                                                                                            |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| `linear` | Default. Standard linear mapping.                                                                                      |
| `log`    | Positive-only. Implemented as symlog with `linearThreshold → 0`.                                                       |
| `symlog` | Handles zero and negative values. Parameters (`linearThreshold`, `base`) are auto-derived from data unless overridden. |

`log` is not a separate implementation — it is the symlog special case. The auto-derivation for
symlog picks `linearThreshold = median(|nonzero values|) / 100` and `base = 10`, both overridable
per axis.

### Axis Tick Generation

Target tick count is 5–8 per axis, computed from the axis pixel length (approximately one tick per
60 px). Algorithm per scale type:

- **Linear** — standard "nice numbers": ticks at multiples of `1 | 2 | 5 × 10^n` where n is chosen
  so the step covers roughly 1/6 of the visible range.
- **Symlog** — ticks at each integer power of `base` within the log region (e.g., ±1, ±10, ±100),
  plus linear ticks within the `linearThreshold` band near zero.
- **Log** — same as symlog with the linear band collapsed to zero.

Tick labels use `Intl.NumberFormat` with `notation: 'compact'` as the default formatter. A
`tickFormat` callback on `ScaleConfig` overrides this per axis.

---

## Special Value Handling

The library treats `NaN`, `+Infinity`, and `-Infinity` as first-class values rather than silently
dropping them.

- **NaN** — breaks the path (lifts the pen) so adjacent segments are not connected. A small
  configurable marker (default: an `×` glyph) is drawn on the highlight canvas at the NaN x-position
  at the axis baseline.
- **+Infinity** — clamped to the top of the plot area; a directional marker (↑ arrow) is drawn at
  the series color on the highlight canvas.
- **-Infinity** — clamped to the bottom of the plot area; a directional marker (↓ arrow) is drawn.
- **Outlier detection** — a per-series flag enables IQR-based outlier highlighting. Outlier points
  are drawn in a contrasting color on the highlight canvas. The IQR computation happens once at data
  ingestion, not per frame.

---

## Data Model

### Input Format

```ts
type SeriesData = {
  id: string; // stable, caller-assigned cache key
  x: Float64Array; // monotonically increasing; no NaN/Inf
  y: Float64Array; // same length as x; may contain NaN/±Inf
  yLow?: Float64Array; // band lower bound (same length)
  yHigh?: Float64Array; // band upper bound (same length)
  renderAs?: RenderAs; // 'line' | 'points' | 'band'; see defaults below
  style?: SeriesStyle;
  highlightOutliers?: boolean; // default false
};

type SeriesStyle = {
  color?: string; // CSS color string; auto-assigned from palette if omitted
  strokeWidth?: number; // device px; default 1.5 (line), 0 (points), 1 (band border)
  pointRadius?: number; // device px; default 3 in 'points' mode
  opacity?: number; // 0–1; applies to main canvas draw; default 1
  fillOpacity?: number; // band fill alpha; default 0.15
};

type ScaleConfig = {
  type?: "linear" | "log" | "symlog"; // default 'linear'
  min?: number; // override auto-derived domain min
  max?: number; // override auto-derived domain max
  linearThreshold?: number; // symlog only; auto-derived if omitted
  base?: number; // symlog/log; default 10
  tickFormat?: (value: number) => string;
};

type ControllerState = {
  xWindow: [number, number];
  highlightedSeriesIds: Set<string>;
  crosshairX: number | null;
};

type RenderAs = "line" | "points" | "band";
```

`Float64Array` is required (not `number[]`). This enables zero-copy views into WASM or
worker-computed buffers and avoids V8 array polymorphism.

Default `renderAs`: `'band'` when `yLow`/`yHigh` are present, `'line'` otherwise.

### Series Color Palette

When `style.color` is omitted, colors are auto-assigned sequentially from a built-in 10-color
categorical palette (similar to Tableau 10). The palette cycles if there are more than 10 series.
Palette entries are stable by series insertion order within a chart, not by `id`.

### Data Normalization

On ingestion each series is validated:

- `x` must be finite (no NaN/Inf in x).
- `x` must be monotonically non-decreasing; if not, it is sorted (along with corresponding y values)
  once and cached.
- `yLow` / `yHigh` presence is validated: both must be present or neither.

Validation errors are reported via a configurable `onError` callback; they do not throw by default.

---

## Shared Controller

A `ChartController` instance is the single source of truth for inter-chart state: the visible X
window, highlighted series IDs, and active crosshair position.

### Reactive-Only Updates

The controller is **reactive-only**: it never pushes an initial synchronization event when a chart
mounts. Charts read current controller state synchronously during their first render (via a ref), so
they start in the correct state without waiting for an effect. This eliminates the "async blink
storm" where all charts briefly render with default zoom before jumping to the shared zoom level.

```ts
class ChartController {
  // Observable state (MiniSignal or equivalent tiny reactive primitive)
  xWindow: [number, number];
  highlightedSeriesIds: Set<string>;
  crosshairX: number | null;

  // Mutators — synchronously update state and notify subscribers
  setXWindow(window: [number, number]): void;
  setHighlight(ids: Set<string>): void;
  setCrosshairX(x: number | null): void;

  subscribe(listener: () => void): () => void;
}
```

The controller uses a minimal internal reactive primitive (no external dep). React integration uses
`useSyncExternalStore` so updates are batched correctly under React 18 concurrent mode.

---

## React API

### `<Chart>`

```tsx
<Chart
  series={SeriesData[]}
  width={number}                // optional; defaults to container width
  height={number}
  controller={ChartController} // optional; unlinked chart if omitted
  xScale?: ScaleConfig
  yScale?: ScaleConfig
  onSeriesHover?: (id: string | null) => void
  onPointClick?: (seriesId: string, index: number) => void
  className?: string
  style?: CSSProperties
/>
```

### `useChartController`

```ts
function useChartController(initial?: Partial<ControllerState>): ChartController;
```

Creates a stable `ChartController` instance scoped to the calling component's lifetime. Passing the
same instance to multiple `<Chart>` components synchronizes them.

---

## Interaction Model

### Zoom

- **Click-drag** on the plot area draws a zoom rectangle (highlight canvas + DOM overlay border) and
  zooms to that X range on pointer-up.
- **Scroll wheel** zooms in/out centered on the cursor X position. Scroll events are throttled to
  `requestAnimationFrame` to prevent queuing more redraws than the display can consume.
- Both interactions update `controller.xWindow`, which propagates to all linked charts.
- A **reset zoom** button (rendered in the DOM overlay) restores the full data domain (union of all
  series' x ranges).
- **Zoom limits** — minimum zoom: the window must span at least 2 distinct x values in any series
  (prevents sub-point zoom). Maximum zoom-out: the window cannot exceed the full data domain.

### Crosshair and Data Point Lookup

Pointer movement over any linked chart updates `controller.crosshairX`. All linked charts draw a
vertical crosshair line on their highlight canvas at the corresponding data-space X coordinate.

The nearest data point per series is found via **binary search on the sorted x array** (O(log n) per
series). The closest point by x distance is marked with a filled circle on the highlight canvas. A
tooltip anchor `<div>` is positioned at the nearest point's canvas coordinates; callers render
tooltip content into it via a React portal or the `onSeriesHover` callback.

### Hover Highlight

Hovering within configurable proximity of a series (default: 8 CSS px from the nearest rendered
pixel of the path) sets `controller.highlightedSeriesIds`. Highlighted series are drawn at full
opacity on the highlight canvas; non-highlighted series are dimmed (overlay with semi-transparent
fill on highlight canvas — no main canvas redraw).

---

## Performance Constraints

- No client-side decimation. The caller is responsible for providing pre- aggregated data at an
  appropriate resolution for the current zoom level.
- Main canvas redraws are triggered only by: data change, zoom/pan, resize.
- Highlight canvas redraws are triggered by pointer events; they must complete within one animation
  frame (~16 ms at 60 Hz) for 100k points across all visible charts.
- `Path2D` compilation for 100k points must complete in < 50 ms on a mid-range 2024 laptop
  (measured, not estimated).
- Off-viewport charts incur zero render cost after initial mount.
- Y-domain recalculation on zoom is bounded by the number of points in the visible X window, not the
  total series length.

---

## Environment Requirements

- **React** ≥ 18.0 (`useSyncExternalStore` is used without a polyfill).
- **Browsers**: Chrome 88+, Firefox 78+, Safari 15.4+. These are the earliest versions with complete
  support for `Path2D`, `DOMMatrix`, `IntersectionObserver`, `ResizeObserver`, and pointer events.
- No IE or legacy Edge support.
- No Node.js / SSR compatibility (Canvas APIs are browser-only by design).

---

## Risks, Assumptions, and Open Questions

### Risks

- **Floating-point precision at extreme zoom** — when `xWindow` spans a very narrow range relative
  to the data domain (e.g., zooming into a region where x values differ by 1e-15), affine transform
  coefficients may overflow float32 precision in the `DOMMatrix`. Mitigation: the minimum zoom limit
  (≥ 2 distinct x values) reduces exposure; the normalized-coordinate scheme keeps path data in
  [0,1] regardless of absolute x magnitude.
- **Main-thread render spike on rapid viewport entry** — if the user scrolls quickly past 20+
  off-viewport charts, all may enter the viewport within a single frame and attempt to compile paths
  simultaneously. Mitigation: `IntersectionObserver` callbacks are batched by the browser; renders
  should be scheduled via `requestIdleCallback` for charts that are newly entering rather than
  already visible.
- **Canvas memory** — 100+ charts × 2 canvases × high DPR ≈ significant pixel buffer allocation. At
  4k DPR-2 with a raster cap of 16 MP each, 100 charts × 2 canvases = 200 buffers × ~64 MB each is
  clearly too high; the raster cap must be respected and the default chosen conservatively.

### Assumptions

- Server always provides data pre-aggregated to an appropriate zoom level; the library makes no
  network requests and has no data-fetching layer.
- Callers manage series ID stability across re-renders; the cache provides no benefit if IDs change
  on every render.
- React 18 concurrent mode is the deployment target; React 17 and legacy mode are not tested.

### Open Questions

- **Y-axis sharing** — should the controller optionally synchronize Y windows across linked charts
  (useful for comparing series on the same scale)? Currently Y is always per-chart. Deferred to a
  future API addition.
- **Cache memory limit default** — 2 000 paths is a placeholder; the right number depends on average
  path complexity. Should be validated against the 100+ chart scenario before finalizing.
- **`requestIdleCallback` for off-viewport render scheduling** — browser support is good but the API
  is not yet standardized. A `setTimeout(fn, 0)` fallback may be sufficient.

---

## Out of Scope

- **SSR / server rendering** — Canvas APIs are browser-only; no Node/edge compatibility layer is
  provided.
- **Accessibility** — No ARIA roles, keyboard navigation, or screen-reader support in v1.
- **Plugins / theming / animations** — No extension points, no CSS custom property theming, no
  enter/exit transitions.
- **Bar, pie, scatter (statistical), categorical charts** — Only line, point, and band series on
  continuous axes.
- **CommonJS output** — ESM only.
- **Touch / mobile gestures** — Pointer events are used (which cover touch), but pinch-zoom and
  swipe-pan are not implemented in v1.
- **Legends** — No built-in legend component; callers render their own using the series `id` and
  `style.color`.
- **Tooltip content** — The library positions a tooltip anchor `<div>` at the nearest data point;
  callers are responsible for rendering content into it. No built-in tooltip UI is provided.
- **Y-axis synchronization** — Controller manages only the X window; Y domains are always
  independent per chart.

---

## Module Exports

```ts
// Primary chart component
export { Chart } from "./Chart";

// Controller
export { ChartController, useChartController } from "./controller";

// Configuration
export { configure } from "./config"; // maxCachedPaths, etc.

// Types
export type { SeriesData, SeriesStyle, ScaleConfig, ControllerState, RenderAs };
```

No default export. Tree-shakeable.
