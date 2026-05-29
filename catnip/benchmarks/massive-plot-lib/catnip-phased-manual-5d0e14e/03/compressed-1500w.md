# PlotLib — Fast Canvas-Based Plotting Library: Spec

## Overview

Zero-dependency, ESM-only, React-peer charting library for ML training dashboards. Core constraint:
100k pts/chart, 100+ charts visible simultaneously, main thread only, no dropped frames.

---

## Supported Chart Types

- **Line** — continuous series; gaps on NaN.
- **Point** (scatter) — discrete markers; ⊘ on NaN.
- **Band** — filled region between a `band-lo`/`band-hi` pair sharing a `bandId`. Both halves must
  share the same `x` array; mismatch suppresses render and issues a console warning. Fill uses
  `band-lo` color at 20% opacity.

---

## Data Model

```ts
interface Series {
  id: string; // stable; cache key
  x: Float64Array; // monotonically increasing, finite
  y: Float64Array; // same length; NaN and ±Infinity allowed
  type: "line" | "point" | "band-lo" | "band-hi";
  bandId?: string;
  color: string;
  width?: number; // CSS px; default 1.5
}
```

Each series has its own `x` array — independent X per series is first-class. NaN/±Inf in `y` are
stored in a `Uint8Array` flags array during normalization; ±Inf render as edge arrows labeled on
hover.

**Pre-aggregation**: caller pre-aggregates to ≤ 100k pts/series. When pts > pixel width, the library
applies a min/max (not LTTB) decimation pass during Path2D construction, preserving extrema for
outlier visibility.

**Data updates**: no append API. Replace the series object with a new one sharing the same `id` but
a new array reference; the changed reference triggers Path2D cache eviction and redraw. Live
dashboards should throttle updates to one per animation frame.

---

## Performance Targets

| Scenario                         | Target                                      |
| -------------------------------- | ------------------------------------------- |
| 100 series × 1 000 pts           | First render ≤ 16 ms                        |
| 1 000 series × 100 pts           | First render ≤ 16 ms                        |
| 1 series × 100 000 pts           | First render ≤ 16 ms                        |
| 100 charts loaded simultaneously | No jank; virtualization limits active draws |
| Zoom/pan                         | ≤ 16 ms re-render                           |
| Crosshair hover                  | ≤ 4 ms repaint                              |

Mid-range laptop (M1/Core i7), hardware-accelerated browser, data pre-normalized.

---

## Axis Scales

**Linear**: default, no special treatment.

**Log**: maps to symlog with auto-derived `linthresh = max(min(|nonzero y|) × 0.1, 1e-6)`, fixed
`linscale = 1.0`; caller may override `linthresh`.

**Symlog**: explicit `linthresh`/`linscale`. Log is a named preset of symlog — both share one code
path. Symlog handles zero and negative values (gradient norms, residuals, signed metrics). Ticks at
powers of 10 in log regions plus linear ticks near zero; formatter switches `1e-3` ↔ decimal
notation by magnitude.

**Y range**: auto-fits to min/max of data visible within the current `xRange` (not all data).
Override with `yRange: [min, max]` prop to fix the axis on zoom/pan. One Y axis per chart; multiple
Y axes are out of scope.

---

## Shared Controller

```ts
interface ControllerState {
  xRange: [number, number] | null; // null = each chart auto-fits to its own extent
  highlightX: number | null;
}
interface SharedController {
  subscribe(listener: () => void): () => void;
  getSnapshot(): ControllerState;
  setXRange(range: [number, number] | null): void;
  setHighlightX(x: number | null): void;
}
```

**Reactive-only protocol**: no `init()` call, no synchronous broadcast on mount. Charts read current
controller state on first render. This avoids async blink storms where batched chart mounts
repeatedly reset shared state. Changes write a new state object; subscribed charts re-render on next
RAF. Off-viewport charts skip re-renders and sync when scrolled back into view.

---

## Rendering Architecture

### Canvas Layering

Two `<canvas>` elements stacked via `position: absolute`:

1. **Main canvas** — series paths; redrawn on data change, zoom, or pan.
2. **Highlight canvas** — crosshair, hovered markers, band hover fill; cleared and redrawn on each
   `mousemove`.

DOM layer above both for axis tick text, zoom-rect `<div>`, and tooltip. Full-chart SVG rejected:
per-element layout scales with point count.

### Draw Scheduling

All main-canvas redraws go through `requestAnimationFrame` with a per-chart dirty flag. Multiple
state changes within one frame coalesce into a single draw. The highlight canvas repaints
synchronously on `mousemove` — exempt from coalescing — to avoid crosshair lag.

### Path2D Caching

Paths are built in **zoom-normalized [0,1]² coordinates**. Cache key:
`(seriesId, xMin, xMax, yMin, yMax, decimationBucketCount)`.
`decimationBucketCount = nextPow2(pixelWidth)` — power-of-2 quantization improves cache hit rate
across small resize events without raw pixel dimensions in the key. On cache hit, the path is drawn
via `ctx.setTransform()` mapping [0,1]² to canvas pixels. LRU, 200 entries/chart; evicted when the
series' array reference changes.

### Data Normalization

One-time per series before any rendering:

1. Scan `y` for NaN, +Inf, −Inf; record indices in `flagsArray: Uint8Array`.
2. Write a normalized copy with flagged values replaced by boundary values.
3. Compute `yMin`, `yMax` over valid values.

Normalized copy drives rendering; original retained for tooltips.

### DPR, Resize, and Raster Cap

`devicePixelRatio` tracked via media query; canvas sized at CSS × DPR. `ResizeObserver` triggers
attribute update + full cache eviction + RAF redraw. Raster cap: effective DPR floored so
`cssSize × DPR ≤ 4096` physical pixels, applied per-axis independently (avoids over-capping short,
wide charts on the Y axis).

### Off-Viewport Virtualization

`IntersectionObserver` — when fully off-viewport, charts skip redraws and release canvas backing
(`canvas.width = 1`) to free GPU memory; normalized data stays in JS memory. Full redraw on
re-entry.

### Rejected Backends

**WebGL**: 16-context browser cap exhausted by 100+ charts; no native wide/dashed lines without
geometry workarounds.

**OffscreenCanvas/Workers**: structured-clone latency is measurable at 100k pts; main-thread meets
all targets without IPC overhead.

---

## Interaction

### Zoom

Click-drag draws an X-only zoom rectangle (DOM div). On release, writes new `xRange` to the
controller (or local state if no controller). Double-click resets to `null` (auto-fit). Scroll wheel
zooms ±10% per tick around cursor X.

### Pan

Alt+drag or single-touch drag pans the X range. No momentum — precision use, not exploratory
scrolling. Pinch-zoom not supported; touch is single-touch pan only.

### Crosshair and Highlight

`mousemove` → cursor X in data coordinates → binary search on each series' own `x` array →
`highlightX` stored as raw data-coord X, not snapped to any series. Each subscribed chart snaps
independently when rendering. Tooltip lists all series values; NaN and ±Inf display their special
labels.

### Keyboard

- `Escape`: reset zoom to auto-fit.
- Arrow keys (chart focused): pan left/right by 10% of visible range.

---

## React API

```tsx
// Standalone
<Chart series={seriesArray} yScale="symlog" width={600} height={300} />

// Synchronized
const ctrl = useSharedController({ initialXRange: [0, 1000] });
<Chart series={lossSeriesArray} controller={ctrl} />
<Chart series={gradNormArray} controller={ctrl} yScale="log" />
```

`useSharedController` returns a stable reference; charts subscribe on mount and unsubscribe on
unmount. `series` identity is tracked by `id`: same `id` + new array reference = evict that series'
cached paths only; new `id` = full eviction and redraw.

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
  y: number | null; // null for NaN; ±Infinity as Infinity
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

All types exported. No default export.

---

## Build and Distribution

- ESM-only. No CommonJS. Entry: `index.ts` → `dist/index.js` + `dist/index.d.ts`.
- Zero runtime deps. React peer `^18 || ^19`. Target ES2020. Bundler: Vite lib mode or tsup.

---

## Risks, Assumptions, and Open Questions

### Assumptions

- `x`/`y` must be `Float64Array`; plain arrays are not accepted.
- `x` must be monotonically increasing and finite — binary search precondition; violation is
  undefined behavior with no runtime check (O(n) cost per series).
- Hardware-accelerated canvas compositing assumed; stacked canvases degrade to software blending
  without it.

### Risks

- **Memory at scale**: 100 charts × 1M retained pts × 2 Float64Arrays × 8 B ≈ 1.6 GB. Caller must
  pre-aggregate to 100k to stay within bounds.
- **Path2D transform fidelity**: `ctx.setTransform()` reuse of [0,1]² paths may produce sub-pixel
  rounding on some GPU/browser combos; negligible at normal line widths.
- **LRU cache thrash**: 200-entry limit may be insufficient for many series + frequent zoom.
  Mitigate by snapping to discrete zoom levels.
- **Virtualization threshold**: "fully outside viewport" means mostly-offscreen charts still hold
  live canvases.

### Open Questions

- **Multiple Y axes**: callers must use separate charts with synchronized X for mixed-magnitude
  overlays.
- **Decimation bucket quantization**: power-of-2 step is a heuristic; the correct value may need
  empirical tuning.
- **Y-axis zoom**: only X is user-zoomable; `yRange` prop is the workaround but has no built-in drag
  gesture.

---

## Out of Scope

SSR, accessibility, plugins/theming/animations, bar/pie/categorical charts, CommonJS/UMD, multiple Y
axes per chart, Y-axis zoom gesture, touch pinch-zoom, Y-axis cross-chart sync.
