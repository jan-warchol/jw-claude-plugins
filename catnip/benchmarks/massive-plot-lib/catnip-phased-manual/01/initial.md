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

---

## Coordinate Systems

### X-Axis Model

Each series carries its own independent X array. The chart's visible X domain is the union of all
series' X ranges by default, or it can be set explicitly via the shared controller. Independent X
per series allows overlaying series sampled at different frequencies without interpolation or
alignment.

### Scale Types

| Scale    | Description                                                                                                            |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| `linear` | Default. Standard linear mapping.                                                                                      |
| `log`    | Positive-only. Implemented as symlog with `linearThreshold → 0`.                                                       |
| `symlog` | Handles zero and negative values. Parameters (`linearThreshold`, `base`) are auto-derived from data unless overridden. |

`log` is not a separate implementation — it is the symlog special case. The auto-derivation for
symlog picks `linearThreshold = median(|nonzero values|) / 100` and `base = 10`, both overridable
per axis.

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
  x: Float64Array; // monotonically increasing
  y: Float64Array; // same length as x; may contain NaN/±Inf
  yLow?: Float64Array; // band lower bound (same length)
  yHigh?: Float64Array; // band upper bound (same length)
};
```

`Float64Array` is required (not `number[]`). This enables zero-copy views into WASM or
worker-computed buffers and avoids V8 array polymorphism.

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
  width={number}           // optional; defaults to container width
  height={number}
  controller={ChartController}  // optional
  xScale?: ScaleConfig
  yScale?: ScaleConfig
  highlightOutliers?: boolean   // default false
  onSeriesHover?: (id: string | null) => void
  className?: string
  style?: CSSProperties
/>
```

### `<Band>` / `<Line>` / `<Points>` (series renderers)

Series rendering style is determined by the presence of `yLow`/`yHigh` (band), or by an explicit
`renderAs` prop on each series data object:

```ts
type RenderAs = "line" | "points" | "band";
```

Default: `'line'` when only `y` is present, `'band'` when `yLow`/`yHigh` are present.

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
- **Scroll wheel** zooms in/out centered on the cursor X position.
- Both interactions update `controller.xWindow`, which propagates to all linked charts.
- A **reset zoom** button (rendered in the DOM overlay) restores the full data domain.

### Crosshair

Pointer movement over any linked chart updates `controller.crosshairX`. All linked charts draw a
vertical crosshair line on their highlight canvas at the corresponding data-space X coordinate. The
nearest data points on each series are marked with a circle.

### Hover Highlight

Hovering within configurable proximity of a series sets `controller.highlightedSeriesIds`.
Highlighted series are drawn at full opacity on the highlight canvas; non-highlighted series are
dimmed (overlay with semi-transparent fill on highlight canvas — no main canvas redraw).

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

---

## Module Exports

```ts
// Primary chart component
export { Chart } from "./Chart";

// Controller
export { ChartController, useChartController } from "./controller";

// Types
export type { SeriesData, ScaleConfig, ControllerState, RenderAs };
```

No default export. Tree-shakeable.
