# PlotLib — Fast Canvas-Based Plotting Library: Spec

## Overview

A zero-dependency, ESM-only, React-peer charting library targeting ML training dashboards. Primary
design constraint: render 100k data points per chart and keep 100+ charts visible simultaneously,
without blocking the main thread or dropping frames.

The design sits between uPlot (raw speed, limited API) and Dygraphs (rich API, heavier). The goal is
to match uPlot on throughput and Dygraphs on interactivity, for the specific chart types needed in
loss/metric monitoring.

---

## Supported Chart Types

- **Line** — continuous series connecting sampled points.
- **Point** (scatter) — discrete markers; renders even when there are too few points for a line.
- **Band** — a shaded region between two Y series sharing the same X; used for confidence intervals,
  min/max envelopes.

Bar, pie, and categorical charts are explicitly out of scope.

---

## Data Model

### Series

Each series is an object:

```ts
interface Series {
  id: string; // stable; used as cache key
  x: Float64Array; // monotonically increasing timestamps/steps
  y: Float64Array; // same length as x; NaN and ±Infinity allowed
  type: "line" | "point" | "band-lo" | "band-hi";
  bandId?: string; // required for band-lo/band-hi; pairs the two halves
  color: string; // CSS color string
  width?: number; // stroke width in CSS px; default 1.5
}
```

Each series carries its own `x` array. Multiple series in a chart do **not** need to share an X axis
— independent X per series is first-class.

A band is formed by pairing one `band-lo` and one `band-hi` series that share the same `bandId`.
Both halves must have the same `x` array (same length, same values). If they differ, the band is not
rendered and a console warning is issued. Band fill uses the `color` of the `band-lo` series at 20%
opacity.

### NaN and ±Infinity

- **NaN** in `y`: rendered as a visible gap in line charts; a distinct hollow marker (⊘) in point
  charts.
- **+Infinity / −Infinity**: rendered as an arrow glyph at the top or bottom axis edge respectively;
  labeled on hover.
- These special values are detected during data normalization (see below) and stored in a separate
  `flagsArray: Uint8Array`, not inlined into the draw path.

### Pre-aggregation Contract

The library does no server-side decimation. The caller is expected to pre-aggregate to ≤ 100k points
per series before passing data. The library's own downsampling is limited to one case: when the
chart pixel width is known and the series has more points than pixels, a min/max envelope decimation
pass is applied client-side during Path2D construction (see Rendering). This is a min/max pass, not
LTTB — it preserves extrema (outlier visibility) at the cost of slightly higher line roughness. For
1M-point series the caller must supply pre-aggregated data; the library can hold up to ~1M raw
points in memory but will not render more than 100k per draw call without explicit opt-in
decimation.

### Data Updates

The library does not expose an append API. To update a series (e.g., new training steps arriving),
replace the series object with a new one carrying the same `id` and updated `x`/`y` arrays. The
renderer detects the changed array reference, evicts cached paths for that `id`, and redraws.
Callers should reuse the typed array allocation where possible (e.g., swap in a longer buffer) to
reduce GC pressure, but the array reference must change for cache invalidation to fire.

Streaming / live-updating dashboards should throttle updates to at most one per animation frame per
chart (16 ms). The library does not enforce this; it is the caller's responsibility.

---

## Scaling and Performance Targets

| Scenario                                  | Target                                                   |
| ----------------------------------------- | -------------------------------------------------------- |
| Single chart, 100 series × 1 000 pts each | First render ≤ 16 ms                                     |
| Single chart, 1 000 series × 100 pts each | First render ≤ 16 ms                                     |
| Single chart, 1 series × 100 000 pts      | First render ≤ 16 ms                                     |
| 100 charts loaded simultaneously          | No jank on page load; virtualization limits active draws |
| Zoom interaction (pan/zoom)               | ≤ 1 frame (16 ms) re-render for visible charts           |
| Crosshair hover                           | ≤ 4 ms highlight repaint                                 |

These targets are on a mid-range laptop (M1 / Core i7 class) in a browser with hardware acceleration
enabled. They assume the data is already normalized (see Data Normalization).

---

## Axis Scales

### Linear

Default. No special treatment.

### Log

`type: 'log'` on an axis. Internally maps to symlog with `linthresh` computed automatically:

- `linthresh = min(abs(nonzero values)) * 0.1`, or `1e-6` whichever is larger.
- `linscale = 1.0` (fixed).
- The caller may override `linthresh` explicitly.

### Symlog

`type: 'symlog'` with optional `linthresh` and `linscale`. Log is just a named preset of symlog.
This collapses the two concepts into one code path. Symlog handles zero and negative values, making
it appropriate for gradient norms, residuals, and signed metrics.

Tick placement on symlog: ticks are generated at powers of 10 in the log regions plus a handful of
linear ticks near zero. The tick formatter switches between exponential (`1e-3`) and decimal
notation based on magnitude.

### Y Range and Auto-Fit

By default the Y range auto-fits to the min/max of the **visible** data — i.e., only points whose
`x` falls within the current `xRange`. This keeps the Y axis scaled to what is on screen, which is
more useful than fitting to all data when zoomed into a region.

A `yRange` prop on `ChartProps` overrides auto-fit with a fixed `[min, max]` interval. When set, the
Y axis does not adjust on zoom/pan.

Only one Y axis per chart is supported. Multiple independent Y axes are out of scope.

---

## Shared Controller

The shared controller manages synchronized zoom, pan, and highlight state across a set of charts.

```ts
interface ControllerState {
  xRange: [number, number] | null; // null = auto-fit per chart
  highlightX: number | null;
}

interface SharedController {
  subscribe(listener: () => void): () => void;
  getSnapshot(): ControllerState;
  setXRange(range: [number, number] | null): void;
  setHighlightX(x: number | null): void;
}
```

**Reactive-only protocol.** The controller is a value object; consumers subscribe to it via a
standard React context or a framework-agnostic subscribe/notify interface. There is no imperative
`init()` call and no synchronous broadcast on mount. Charts that mount after the controller is set
read the current state on their first render. This avoids the "async blink storm" pattern where a
batch of chart mounts each fire an init event that briefly resets shared state.

Zoom/pan changes by one chart are written to the controller as a new state object; all subscribed
charts re-render on their next animation frame. Charts that are off-viewport (virtualized) skip the
re-render and pick up the latest state when they scroll back into view.

When `xRange` is `null`, each chart auto-fits to its own data extent independently.

---

## Rendering Architecture

### Canvas Layering

Each chart instance creates two `<canvas>` elements stacked via CSS `position: absolute`:

1. **Main canvas** — draws all series paths. Redrawn on zoom/pan or data change.
2. **Highlight canvas** — draws crosshair line, hovered point markers, and band hover fill. Redrawn
   on every `mousemove`. Cleared before each repaint with `clearRect`.

A single DOM layer sits above both canvases for:

- Axis labels and tick text (positioned `<span>` elements or a single SVG per axis).
- Zoom rectangle drag (a `<div>` with `pointer-events: auto`).
- Tooltip (absolutely positioned `<div>`).

This layering eliminates the need to repaint the main canvas during crosshair hover — the most
frequent operation.

**SVG for the full chart is rejected.** SVG path elements impose per-element layout and style
recalculation costs that scale linearly with point count, making it unsuitable for 100k-point
series.

### Draw Scheduling

All redraws are scheduled through `requestAnimationFrame`. Each chart maintains a dirty flag. When
state changes (new data, zoom, pan, resize), the flag is set and a RAF callback is registered;
subsequent state changes before the next frame are coalesced. The RAF callback clears the flag and
executes the draw. This prevents multiple full redraws within a single frame when several state
changes arrive together (e.g., controller update + resize).

The highlight canvas is exempt from dirty-flag coalescing: it repaints synchronously on `mousemove`
to avoid crosshair lag.

### Path2D Caching

Paths are built in **zoom-normalized coordinates**: X and Y data values are mapped to [0, 1] based
on the series' local extent at construction time. The `Path2D` object is cached keyed by
`(seriesId, xMin, xMax, yMin, yMax, decimationBucketCount)`.

`decimationBucketCount` is the number of min/max buckets used during the client-side decimation
pass. It is derived from `floor(pixelWidth / 1)` (one bucket per CSS pixel) but quantized to the
nearest power of 2 to improve cache hit rate across small resize events. The key does not include
raw `pixelWidth`/`pixelHeight` so that identical viewport ranges but slightly different pixel
dimensions (e.g., a 1px resize) still hit the cache.

On pan/zoom, the path for the new `(xMin, xMax, yMin, yMax)` is looked up. If found, it is drawn via
`ctx.setTransform()` mapping [0,1]² to canvas pixels — a matrix multiply, not a path rebuild. If not
found, the path is reconstructed and cached.

Cache invalidation: when series data is replaced (changed `y` array reference), all cached paths for
that series `id` are evicted.

Cache size limit: 200 entries per chart (LRU). Exceeding this discards the least-recently-used path.

### Data Normalization

Before any rendering, each series goes through a one-time normalization pass:

1. Scan `y` for NaN, +Infinity, −Infinity; record indices in `flagsArray: Uint8Array`.
2. Replace flagged values in a copy of `y` with the series' local min/max (for path continuity) or
   with the clip boundary, depending on the flag type.
3. Compute `yMin`, `yMax` over the valid values.
4. Store the normalized copy alongside the original.

The normalized copy is what Path2D construction reads. The original is retained for tooltip display.

### DPR and Resize

`devicePixelRatio` is read once on mount and on `window` `devicePixelRatio` media query change
events. The canvas `width`/`height` attributes are set to CSS size × DPR; `ctx.scale(DPR, DPR)` is
applied once after each resize.

`ResizeObserver` watches the chart container. On resize, the canvas attributes are updated, all
cached paths for this chart are evicted, and a new draw is scheduled via the RAF dirty-flag system.

### Raster Cap

A raster cap limits the maximum canvas backing size to prevent GPU texture allocation failures on
high-DPR screens with large charts. Default cap: `4096 × 4096` physical pixels. If
`cssWidth * DPR > 4096`, the DPR used for this axis is floored to `floor(4096 / cssWidth)`. This is
applied per-axis independently so a very wide, short chart is not over-capped on the Y axis.

### Off-Viewport Virtualization

Charts register with a shared `IntersectionObserver`. When a chart's root element is fully outside
the viewport, it:

- Skips re-renders from controller state updates.
- Releases its main canvas backing store (sets `canvas.width = 1`) to free GPU memory.
- Retains its data and normalized series in JS memory.

On re-entry into the viewport, the canvas is resized and a full redraw is scheduled on the next
animation frame.

### WebGL and OffscreenCanvas

**WebGL is rejected.** Browsers cap WebGL contexts at 16 per page. 100+ charts would exhaust this
immediately. WebGL also lacks native wide-line and dashed-line primitives — implementing them
requires geometry shaders or triangle strips, which negates the API simplicity goal.

**OffscreenCanvas / Web Workers are rejected.** Transferring point data to a worker via structured
clone or `SharedArrayBuffer` introduces serialization latency proportional to series size. For
100k-point series this is measurable. The main-thread canvas pipeline stays below the frame budget
without workers, so the complexity is not justified.

---

## Interaction

### Zoom

Click-drag on the chart area draws a zoom rectangle (DOM div, X-axis only — Y is not user-zoomable).
On drag-end:

- If a shared controller is present, writes the new `xRange` to it; all subscribed charts zoom
  together.
- If no controller, updates local state only.

Double-click resets zoom to auto-fit (`xRange = null`).

Scroll wheel zooms around the cursor X position by ±10% per tick.

### Pan

Click-drag while holding `Alt` (or single-touch drag) pans the X range. Velocity-based momentum is
not implemented — the target is precision dashboard use, not exploratory scrolling. Two-finger pinch
zoom on touch is not supported in v1; touch interaction is limited to single-touch pan.

### Crosshair and Highlight

`mousemove` over the chart computes the hovered X position in data coordinates. For each series, the
nearest point is found via binary search on that series' own `x` array (since X arrays are
independent per series). The `highlightX` value written to the controller is the raw cursor X in
data coordinates, not snapped to any series. Each chart snaps independently to its nearest point
when rendering.

Tooltip: a DOM div positioned above/below the crosshair showing series name, x-value, y-value. NaN
and ±Inf display their special labels. When multiple series are present, all visible series values
at the highlighted X are listed.

### Keyboard

- `Escape`: reset zoom to auto-fit.
- Arrow keys (when chart is focused): pan left/right by 10% of visible range.

---

## React API

```tsx
import { Chart, useSharedController } from 'plotlib';

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

`useSharedController` returns a stable controller reference. Charts subscribe on mount and
unsubscribe on unmount. The hook owns no timers; it only updates React state on controller change
events, triggering re-renders.

`series` identity comparison is by `id` field. Changing a series' `id` triggers full path eviction
and redraw. Mutating `y` without changing the array reference is unsupported — always produce a new
`Float64Array` to trigger cache invalidation.

---

## API Surface (TypeScript)

```ts
type ScaleType = "linear" | "log" | "symlog";

interface Series {
  id: string;
  x: Float64Array;
  y: Float64Array;
  type: "line" | "point" | "band-lo" | "band-hi";
  bandId?: string;
  color: string;
  width?: number;
}

interface HoveredPoint {
  seriesId: string;
  x: number;
  y: number | null; // null for NaN; ±Infinity represented as Infinity
  flags: "nan" | "pos-inf" | "neg-inf" | null;
}

interface ControllerState {
  xRange: [number, number] | null;
  highlightX: number | null;
}

interface ChartProps {
  series: Series[];
  xScale?: ScaleType;
  yScale?: ScaleType;
  ySymlogThreshold?: number;
  yRange?: [number, number];
  width?: number | "auto";
  height?: number | "auto";
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

## Risks, Assumptions, and Open Questions

### Assumptions

- Data is passed as `Float64Array`. Callers using plain `number[]` must convert; the library does
  not accept plain arrays.
- `x` arrays are monotonically increasing and finite (no NaN/Inf in X). This is required for binary
  search correctness. Violation is undefined behavior; no runtime check is performed (it would cost
  O(n) per series).
- The browser has hardware-accelerated canvas compositing. Without it, the stacked-canvas approach
  degrades to software blending, which is slower but still correct.

### Risks

- **Memory at scale.** 100 charts × 1M retained points × 2 Float64Arrays (original + normalized) × 8
  bytes ≈ 1.6 GB. In practice, the caller should pre-aggregate to 100k before passing data. The
  library cannot enforce this limit; callers must govern data size.
- **Path2D transform fidelity.** Drawing a [0,1]² path via `ctx.setTransform()` has been observed to
  produce sub-pixel rounding differences vs. paths built in pixel coords on some browser/GPU
  combinations. The visual impact is negligible for line charts but may produce slightly ragged
  edges on very thin lines.
- **LRU cache size.** The 200-entry-per-chart limit is a heuristic. A chart with many series and
  frequent zoom activity could thrash the cache. Callers can work around this by stabilizing zoom
  increments (snapping to predefined zoom levels).
- **`IntersectionObserver` threshold.** The virtualization threshold is "fully outside viewport." A
  chart that is 1px visible but mostly off-screen still holds a live canvas. For dashboards with
  many partially-visible charts, this may reduce the benefit of virtualization.

### Open Questions

- **Multiple Y axes.** The current design supports one Y axis per chart. Some ML dashboards overlay
  metrics with very different magnitudes (e.g., loss and learning rate on the same chart). This is
  not addressed; callers must use separate charts with synchronized X.
- **Decimation cache key quantization.** The power-of-2 quantization of `decimationBucketCount` is a
  heuristic tradeoff between cache hit rate and rendering fidelity at non-power-of-2 widths. The
  correct quantization step may need empirical tuning.
- **Y-axis zoom.** Only X is user-zoomable. If a use case requires Y zoom, the `yRange` prop
  provides a workaround but with no built-in drag gesture.

---

## Out of Scope

- SSR / server-side rendering.
- Accessibility (ARIA, keyboard-navigable data points).
- Plugin or theming systems.
- Animations or transitions.
- Bar, pie, histogram, or categorical charts.
- CommonJS or UMD bundles.
- Y-axis synchronization (only X is synchronized across charts).
- Multiple Y axes per chart.
- Touch pinch-zoom (single-touch pan only).
