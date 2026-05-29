# PlotLib — Canvas-Based High-Performance Plotting Library

## Purpose

Zero-dependency, ESM-only React library for line, point, and band charts at ML-dashboard scale:
hundreds of simultaneously visible charts, each showing pre-aggregated time-series data. Throughput
target: uPlot. Responsiveness target: Dygraphs. No client-side decimation.

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

Each chart: two `<canvas>` elements + a DOM overlay, absolutely positioned and identically sized:

1. **Main canvas** — persistent series paths; redrawn only on zoom change or data update.
2. **Highlight canvas** — hover emphasis, zoom rectangle, point markers; cleared on every pointer
   event.
3. **DOM overlay** — axis ticks/labels, crosshair, tooltip anchor; React-rendered.

### Path2D Caching

Paths compiled into `Path2D` objects in **zoom-normalized coordinates** (`[xMin,xMax]×[yMin,yMax]` →
`[0,1]×[0,1]`). A `DOMMatrix` transform maps the unit square to canvas pixels at draw time —
pan/zoom changes only the matrix, no path recomputation. Cache keys are **stable series ID strings**
(caller-assigned); invalidated only on data change or series add/remove.

### Rendering Pipeline

```
data update or zoom change
  └─ for each visible chart
       ├─ resolve transform matrix (data window → canvas pixels)
       ├─ ctx.setTransform(matrix); ctx.clearRect(…)
       └─ for each series
            ├─ cache miss → compile Path2D → store
            └─ ctx.stroke(cachedPath)
```

Highlight redraws use the same transform but skip caching.

### Memory, Virtualization, and Resize

Global LRU caps the path cache at `MAX_CACHED_PATHS` (default: 2 000); `IntersectionObserver` clears
off-viewport caches eagerly. Off-viewport charts render a size-preserving `<div>` placeholder;
cached paths are retained for instant re-entry. Override the cap via
`configure({ maxCachedPaths })`.

A shared `ResizeObserver` handles all charts. On resize or DPR change: canvas attributes updated to
`layoutSize × DPR`; raster cap clamps DPR if pixel count exceeds `MAX_CANVAS_PIXELS` (default: 16
777 216); affected paths invalidated (stroke widths are device-px-absolute).

### Rejected Rendering Backends

- **WebGL** — 16-context browser limit; no native wide lines or dashes.
- **OffscreenCanvas / Workers** — `ImageBitmap` IPC cost eliminates the benefit; zoom-state sync
  compounds it.
- **SVG** — layout degrades with 100k DOM nodes regardless of render approach.

---

## Coordinate Systems

### X-Axis

Each series has an independent X array. Chart X domain defaults to the union of all series X ranges;
set explicitly via the controller. Allows overlaying series at different sampling frequencies
without interpolation.

### Y-Domain

Per-chart and auto-derived — not part of the controller. Default: min/max of y values whose x falls
within `xWindow`, so outliers outside the zoomed region don't compress the visible range. Override
with `ScaleConfig.min`/`max`. Recalculated synchronously per redraw via binary search on sorted x
(cost scales with visible point density, not series length).

### Scale Types

| Scale    | Description                                                         |
| -------- | ------------------------------------------------------------------- | --------- | -------------------- |
| `linear` | Default.                                                            |
| `log`    | Positive-only. Symlog with `linearThreshold → 0`.                   |
| `symlog` | Handles zero and negatives. Auto-derives `linearThreshold = median( | nonzero y | )/100`, `base = 10`. |

### Axis Tick Generation

Target 5–8 ticks per axis (~1 per 60 px):

- **Linear** — nice numbers: multiples of `1 | 2 | 5 × 10^n`.
- **Symlog** — powers of `base` in the log region plus linear ticks within the `linearThreshold`
  band.
- **Log** — same as symlog with the linear band collapsed to zero.

Default label format: `Intl.NumberFormat` compact notation. Override per axis via
`ScaleConfig.tickFormat`.

---

## Special Value Handling

`NaN`, `+Infinity`, and `-Infinity` are first-class, not silently dropped.

- **NaN** — lifts the pen; `×` marker drawn on the highlight canvas at the axis baseline.
- **+Infinity** — clamped to top; ↑ marker in series color.
- **-Infinity** — clamped to bottom; ↓ marker.
- **Outlier detection** — per-series flag; IQR computed once at ingestion; outliers drawn in a
  contrasting color on the highlight canvas.

---

## Data Model

```ts
type SeriesData = {
  id: string; // stable, caller-assigned cache key
  x: Float64Array; // monotonically increasing; no NaN/Inf
  y: Float64Array; // may contain NaN/±Inf
  yLow?: Float64Array; // band lower bound (both or neither)
  yHigh?: Float64Array; // band upper bound
  renderAs?: RenderAs; // default: 'band' if yLow/yHigh present, else 'line'
  style?: SeriesStyle;
  highlightOutliers?: boolean; // default false
};

type SeriesStyle = {
  color?: string; // auto-assigned from 10-color palette if omitted
  strokeWidth?: number; // device px; default 1.5 (line), 0 (points), 1 (band border)
  pointRadius?: number; // device px; default 3
  opacity?: number; // default 1
  fillOpacity?: number; // band fill alpha; default 0.15
};

type ScaleConfig = {
  type?: "linear" | "log" | "symlog"; // default 'linear'
  min?: number;
  max?: number; // override auto-derived domain bounds
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

`Float64Array` required (not `number[]`): zero-copy WASM buffer views and V8 monomorphism. Colors
auto-cycle through a 10-color palette by insertion order when `style.color` is omitted.

**Normalization on ingestion:** `x` must be finite and non-decreasing (sorted if not);
`yLow`/`yHigh` must both be present or absent. Violations reported via `onError` callback; no throw.

---

## Shared Controller

`ChartController` is the single source of truth for inter-chart state. **Reactive-only:** no initial
sync event on mount — charts read state synchronously via ref on first render, eliminating the async
blink storm.

```ts
class ChartController {
  xWindow: [number, number];
  highlightedSeriesIds: Set<string>;
  crosshairX: number | null;

  setXWindow(window: [number, number]): void;
  setHighlight(ids: Set<string>): void;
  setCrosshairX(x: number | null): void;
  subscribe(listener: () => void): () => void;
}
```

Uses a minimal internal reactive primitive (no external dep). React integration via
`useSyncExternalStore` for concurrent-mode batching.

```ts
function useChartController(initial?: Partial<ControllerState>): ChartController;
// Stable instance; share across <Chart>s to synchronize them.
```

---

## React API

```tsx
<Chart
  series={SeriesData[]}
  height={number}
  width={number}                // optional; defaults to container width
  controller={ChartController} // optional; unlinked if omitted
  xScale?: ScaleConfig
  yScale?: ScaleConfig
  onSeriesHover?: (id: string | null) => void
  onPointClick?: (seriesId: string, index: number) => void
  className?: string
  style?: CSSProperties
/>
```

---

## Interaction Model

**Zoom** — click-drag draws rect (commits on pointer-up); scroll wheel zooms at cursor
(rAF-throttled). Both write `controller.xWindow`. Reset button restores full data domain. Limits: ≥
2 distinct x values; cannot exceed full domain.

**Crosshair** — pointer movement writes `controller.crosshairX`; all linked charts draw a vertical
line and mark the nearest point per series (binary search on sorted x). Tooltip anchor `<div>`
positioned at nearest point; callers render content into it.

**Hover highlight** — within 8 CSS px of a series, `controller.highlightedSeriesIds` is updated.
Highlighted series at full opacity; others dimmed via highlight-canvas overlay — no main-canvas
redraw.

---

## Performance Constraints

- No client-side decimation; caller pre-aggregates per zoom level.
- Main canvas: redraws on data change, zoom/pan, or resize only.
- Highlight canvas: must complete within 1 rAF (~16 ms at 60 Hz) for 100k pts across all visible
  charts.
- `Path2D` compilation for 100k pts: < 50 ms on a mid-range 2024 laptop (measured).
- Off-viewport charts: zero render cost after mount.
- Y-domain recalculation bounded by visible point density, not total series length.

---

## Environment Requirements

- **React** ≥ 18.0 (`useSyncExternalStore`, no polyfill).
- **Browsers:** Chrome 88+, Firefox 78+, Safari 15.4+ (`Path2D`, `DOMMatrix`,
  `IntersectionObserver`, `ResizeObserver`, pointer events).
- No IE, legacy Edge, Node.js, or SSR support.

---

## Risks, Assumptions, and Open Questions

**Risks:**

- _Float precision at extreme zoom_ — narrow `xWindow` may lose precision in `DOMMatrix` float32
  coefficients. Mitigated by the ≥2-point zoom minimum and [0,1] normalized path coordinates.
- _Render spike on rapid scroll_ — many charts entering the viewport simultaneously may saturate the
  main thread. Schedule newly-visible renders via `requestIdleCallback` (fallback:
  `setTimeout(fn, 0)`).
- _Canvas memory_ — 100+ charts × 2 canvases × high DPR is a significant allocation. Raster cap
  default needs empirical validation.

**Assumptions:** server pre-aggregates data per zoom level; callers maintain stable series IDs.

**Open questions:** optional Y-window sharing via controller (deferred)? Correct `MAX_CACHED_PATHS`
default — 2 000 is a placeholder pending profiling.

---

## Out of Scope

- **SSR / server rendering** — Canvas APIs are browser-only.
- **Accessibility** — No ARIA, keyboard nav, or screen-reader support.
- **Plugins / theming / animations** — No extension points, CSS variable theming, or transitions.
- **Non-continuous chart types** — bar, pie, categorical.
- **CommonJS output** — ESM only.
- **Touch gestures** — pointer events cover touch; pinch-zoom and swipe-pan not implemented.
- **Legends** — callers render their own from `id` and `style.color`.
- **Tooltip content** — anchor `<div>` positioned; content is caller-supplied.
- **Y-axis synchronization** — Y domain is always per-chart.

---

## Module Exports

```ts
export { Chart } from "./Chart";
export { ChartController, useChartController } from "./controller";
export { configure } from "./config";
export type { SeriesData, SeriesStyle, ScaleConfig, ControllerState, RenderAs };
```

No default export. Tree-shakeable.
