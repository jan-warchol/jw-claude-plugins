# PlotLib — Fast Canvas-Based Plotting Library: Spec

## Overview

A zero-dependency, ESM-only, React-peer charting library targeting ML training dashboards.
Primary design constraint: render 100k data points per chart and keep 100+ charts visible simultaneously, without blocking the main thread or dropping frames.

The design sits between uPlot (raw speed, limited API) and Dygraphs (rich API, heavier). The goal is to match uPlot on throughput and Dygraphs on interactivity, for the specific chart types needed in loss/metric monitoring.

---

## Supported Chart Types

- **Line** — continuous series connecting sampled points.
- **Point** (scatter) — discrete markers; renders even when there are too few points for a line.
- **Band** — a shaded region between two Y series sharing the same X; used for confidence intervals, min/max envelopes.

Bar, pie, and categorical charts are explicitly out of scope.

---

## Data Model

### Series

Each series is an object:

```ts
interface Series {
  id: string;          // stable; used as cache key
  x: Float64Array;     // monotonically increasing timestamps/steps
  y: Float64Array;     // same length as x; NaN and ±Infinity allowed
  type: 'line' | 'point' | 'band-lo' | 'band-hi';
  color: string;       // CSS color string
  width?: number;      // stroke width in CSS px; default 1.5
}
```

Each series carries its own `x` array. Multiple series in a chart do **not** need to share an X axis — independent X per series is first-class.

A `band` is formed by pairing one `band-lo` and one `band-hi` series that share a stable `bandId` field. The fill is rendered between them.

### NaN and ±Infinity

- **NaN** in `y`: rendered as a visible gap in line charts; a distinct hollow marker (⊘) in point charts.
- **+Infinity / −Infinity**: rendered as an arrow glyph at the top or bottom axis edge respectively; labeled on hover.
- These special values are detected during data normalization (see below) and stored in a separate flags array, not inlined into the draw path.

### Pre-aggregation Contract

The library does no server-side decimation. The caller is expected to pre-aggregate to ≤ 100k points per series before passing data. The library's own downsampling is limited to one case: when the chart pixel width is known and the series has more points than pixels, a min/max decimation pass is applied client-side during Path2D construction (see Rendering). For 1M-point series the caller must supply pre-aggregated data; the library can hold up to ~1M raw points in memory but will not render more than 100k per draw call without explicit opt-in decimation.

---

## Scaling and Performance Targets

| Scenario | Target |
|---|---|
| Single chart, 100 series × 1 000 pts each | First render ≤ 16 ms |
| Single chart, 1 000 series × 100 pts each | First render ≤ 16 ms |
| Single chart, 1 series × 100 000 pts | First render ≤ 16 ms |
| 100 charts loaded simultaneously | No jank on page load; virtualization limits active draws |
| Zoom interaction (pan/zoom) | ≤ 1 frame (16 ms) re-render for visible charts |
| Crosshair hover | ≤ 4 ms highlight repaint |

These targets are on a mid-range laptop (M1 / Core i7 class) in a browser with hardware acceleration enabled. They assume the data is already normalized (see Data Normalization).

---

## Axis Scales

### Linear

Default. No special treatment.

### Log

`type: 'log'` on an axis. Internally maps to symlog with a threshold `linthresh` computed automatically:

- `linthresh = min(abs(nonzero values)) * 0.1` or `1e-6` whichever is larger.
- `linscale = 1.0` (fixed).
- The caller may override `linthresh` explicitly.

### Symlog

`type: 'symlog'` with optional `linthresh` and `linscale`. Log is just a named preset of symlog. This collapses the two concepts into one code path. Symlog handles zero and negative values, making it appropriate for gradient norms, residuals, and signed metrics.

Tick placement on symlog: ticks are generated at powers of 10 in the log regions plus a handful of linear ticks near zero. The tick formatter switches between exponential (`1e-3`) and decimal notation based on magnitude.

---

## Shared Controller

The shared controller manages synchronized zoom, pan, and highlight state across a set of charts.

```ts
interface SharedController {
  charts: Set<string>;       // chart IDs participating
  xRange: [number, number] | null;   // null = auto-fit
  highlightX: number | null; // hovered X value
}
```

**Reactive-only protocol.** The controller is a value object; consumers subscribe to it via a standard React context or a framework-agnostic subscribe/notify interface. There is no imperative `init()` call and no synchronous broadcast on mount. Charts that mount after the controller is set read the current state on first render. This avoids the "async blink storm" pattern where a batch of chart mounts each fire an init event that briefly resets shared state.

Zoom/pan changes by one chart are written to the controller as a new state object; all subscribed charts re-render on their next animation frame. Charts that are off-viewport (virtualized) skip the re-render and pick up the latest state when they scroll back into view.

---

## Rendering Architecture

### Canvas Layering

Each chart instance creates two `<canvas>` elements stacked via CSS `position: absolute`:

1. **Main canvas** — draws all series paths. Redrawn on zoom/pan or data change.
2. **Highlight canvas** — draws crosshair line, hovered point markers, and band hover fill. Redrawn on every `mousemove`. Cleared before each highlight repaint with `clearRect`.

A single DOM layer sits above both canvases for:
- Axis labels and tick text (positioned `<span>` elements or a single SVG per axis).
- Zoom rectangle drag (a `<div>` with `pointer-events: auto`).
- Tooltip (absolutely positioned `<div>`).

This layering eliminates the need to repaint the main canvas during crosshair hover — the most frequent operation.

### Path2D Caching

Paths are built in **zoom-normalized coordinates**: the X and Y ranges are mapped to [0, 1] at Path2D construction time. The resulting `Path2D` object is cached keyed by `(seriesId, xMin, xMax, yMin, yMax, pixelWidth, pixelHeight)`.

On pan/zoom, if the new viewport maps to a cached key the path is reused. The DOMMatrix transform on `ctx.setTransform()` converts from [0,1]² to canvas pixels at draw time — this is a matrix multiply, not a path rebuild.

Cache invalidation: when series data is replaced (new `id` or same `id` with a changed `y` array reference), all cached paths for that series are evicted. `id` stability is therefore required for efficient updates.

Cache size limit: 200 entries per chart (LRU). Exceeding this discards the least-recently-used path.

### Data Normalization

Before any rendering, each series goes through a one-time normalization pass:

1. Scan `y` for NaN, +Infinity, −Infinity; record indices in a `flagsArray: Uint8Array`.
2. Replace flagged values in a copy of `y` with the series' local min/max (for path continuity) or with the clip boundary, depending on the flag type.
3. Compute `yMin`, `yMax` over the valid values.
4. Store the normalized copy alongside the original.

The normalized copy is what Path2D construction reads. The original is retained for tooltip display.

### DPR and Resize

`devicePixelRatio` is read once on mount and on `window` `devicePixelRatio` media query change events. The canvas `width`/`height` attributes are set to CSS size × DPR; `ctx.scale(DPR, DPR)` is applied once after each resize.

`ResizeObserver` watches the chart container. On resize, the canvas attributes are updated, all cached paths for this chart are evicted (they were built for a different pixel size), and a new draw is scheduled.

### Raster Cap

A raster cap limits the maximum canvas backing size to prevent GPU texture allocation failures on high-DPR screens with large charts. Default cap: `4096 × 4096` physical pixels. If `cssWidth * DPR > 4096`, the DPR used for this axis is floored to `floor(4096 / cssWidth)`. This is applied per-axis independently so a very wide, short chart is not over-capped on the Y axis.

### Off-Viewport Virtualization

Charts register with a shared `IntersectionObserver`. When a chart's root element is fully outside the viewport, it:

- Skips re-renders from controller state updates.
- Releases its main canvas backing store (sets `canvas.width = 1`) to free GPU memory.
- Retains its data and normalized series in JS memory.

On re-entry into the viewport, the canvas is resized and a full redraw is scheduled within the next animation frame.

### WebGL and OffscreenCanvas

**WebGL is rejected.** Browsers cap WebGL contexts at 16 per page. 100+ charts would exhaust this immediately. WebGL also lacks native wide-line and dashed-line primitives — implementing them requires geometry shaders or triangle strips, which negates the API simplicity goal.

**OffscreenCanvas / Web Workers are rejected.** Transferring point data to a worker via structured clone or `SharedArrayBuffer` introduces serialization latency proportional to series size. For 100k-point series this is measurable. The main-thread canvas pipeline stays below the frame budget without workers, so the complexity is not justified.

---

## Interaction

### Zoom

Click-drag on the chart area draws a zoom rectangle (DOM div). On drag-end:

- If a shared controller is present, writes the new `xRange` to it; all subscribed charts zoom together.
- If no controller, updates local state only.

Double-click resets zoom to auto-fit.

Scroll wheel zooms around the cursor X position by ±10% per tick.

### Pan

Click-drag while holding `Alt` (or touch drag) pans the X range. Velocity-based momentum is not implemented — the target is precision dashboard use, not exploratory scrolling.

### Crosshair and Highlight

`mousemove` over the chart computes the nearest data point by binary search on the hovered series' `x` array. Writes `highlightX` to the shared controller (or local state). All charts with the same X domain show a crosshair at that X. The highlight canvas is repainted with the crosshair and nearest-point markers.

Tooltip: a DOM div positioned above/below the crosshair showing series name, x-value, y-value. NaN and ±Inf display their special labels.

### Keyboard

- `Escape`: reset zoom to auto-fit.
- Arrow keys (when chart is focused): pan left/right by 10% of visible range.

---

## React API

```tsx
import { Chart, SharedController, useSharedController } from 'plotlib';

// Standalone chart
<Chart
  series={seriesArray}
  xScale="linear"
  yScale="symlog"
  width={600}
  height={300}
/>

// Synchronized charts
const ctrl = useSharedController({ initialXRange: [0, 1000] });

<Chart series={lossSeriesArray} controller={ctrl} />
<Chart series={gradNormArray} controller={ctrl} yScale="log" />
```

`useSharedController` returns a stable controller reference. Charts subscribe on mount. The hook owns no timers; it only updates React state on controller change events, triggering re-renders.

`series` identity comparison is by `id` field. Changing a series' `id` triggers full path eviction and redraw. Mutating `y` without changing `id` is unsupported — always produce a new series object with the same `id` to get incremental cache behavior.

---

## API Surface (TypeScript)

```ts
// Core types
type ScaleType = 'linear' | 'log' | 'symlog';

interface Series { /* see Data Model */ }

interface ChartProps {
  series: Series[];
  xScale?: ScaleType;
  yScale?: ScaleType;
  ySymlogThreshold?: number;
  width?: number | 'auto';
  height?: number | 'auto';
  controller?: SharedController;
  onZoom?: (xRange: [number, number]) => void;
  onHover?: (x: number, points: HoveredPoint[]) => void;
}

interface SharedController {
  subscribe(listener: () => void): () => void;
  getSnapshot(): ControllerState;
  setXRange(range: [number, number] | null): void;
  setHighlightX(x: number | null): void;
}

function useSharedController(opts?: { initialXRange?: [number, number] }): SharedController;
```

All types are exported. No default export.

---

## Build and Distribution

- **ESM-only**. No CommonJS bundle.
- Single entry point: `index.ts` → `dist/index.js` + `dist/index.d.ts`.
- Zero runtime dependencies. React is a peer dependency (`^18 || ^19`).
- Bundler: Vite library mode or tsup.
- Target: `ES2020` (supports `Float64Array`, `ResizeObserver`, `IntersectionObserver`, `Path2D`).

---

## Out of Scope

- SSR / server-side rendering.
- Accessibility (ARIA, keyboard-navigable data points).
- Plugin or theming systems.
- Animations or transitions.
- Bar, pie, histogram, or categorical charts.
- CommonJS or UMD bundles.
- Y-axis synchronization (only X is synchronized across charts).
