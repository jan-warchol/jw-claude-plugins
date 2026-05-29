# PlotLib — Fast Canvas-Based Plotting Library: Spec

## Overview

Zero-dependency, ESM-only, React-peer charting library for ML training dashboards. Core constraint: 100k pts/chart, 100+ charts visible simultaneously, main thread only.

---

## Supported Chart Types

- **Line** — continuous; gaps on NaN.
- **Point** — discrete markers; ⊘ on NaN.
- **Band** — filled region between a `band-lo`/`band-hi` pair sharing a `bandId`; both halves must share the same `x` array (mismatch suppresses render + console warning). Fill opacity: 20%.

---

## Data Model

```ts
interface Series {
  id: string;        // stable; cache key
  x: Float64Array;   // monotonically increasing, finite
  y: Float64Array;   // NaN and ±Infinity allowed
  type: 'line' | 'point' | 'band-lo' | 'band-hi';
  bandId?: string;
  color: string;
  width?: number;    // CSS px; default 1.5
}
```

Each series has its own `x` array (independent X per series). NaN/±Inf in `y` are stored in a `Uint8Array` flags array; ±Inf render as edge arrows. No append API — replace the series object (same `id`, new array reference) to update; a changed reference invalidates the Path2D cache.

Caller pre-aggregates to ≤ 100k pts/series. Client-side min/max decimation (not LTTB) fires when pts > pixel width. Max 1M pts in memory.

---

## Performance Targets

| Scenario | Target |
|---|---|
| 100 series × 1 000 pts | ≤ 16 ms first render |
| 1 000 series × 100 pts | ≤ 16 ms first render |
| 1 series × 100 000 pts | ≤ 16 ms first render |
| 100 charts loaded | No jank; virtualization limits active draws |
| Zoom/pan | ≤ 16 ms re-render |
| Crosshair hover | ≤ 4 ms repaint |

---

## Axis Scales

**Linear**: default. **Log**: alias for symlog with `linthresh = max(min(|nonzero y|) × 0.1, 1e-6)`, `linscale = 1.0`; caller may override. **Symlog**: `linthresh`/`linscale` explicit. Log and symlog share one code path. Ticks at log powers of 10 + linear near zero; formatter switches notation by magnitude.

**Y range**: auto-fits to min/max of data visible within current `xRange`. Override with `yRange: [min, max]` prop. One Y axis per chart.

---

## Shared Controller

```ts
interface ControllerState {
  xRange: [number, number] | null;  // null = each chart auto-fits independently
  highlightX: number | null;
}
interface SharedController {
  subscribe(listener: () => void): () => void;
  getSnapshot(): ControllerState;
  setXRange(range: [number, number] | null): void;
  setHighlightX(x: number | null): void;
}
```

Reactive-only: no `init()`, no synchronous broadcast on mount — charts read current state on first render (avoids async blink storms on batched mount). Off-viewport charts skip re-renders; they sync on scroll-back.

---

## Rendering Architecture

**Canvas layering**: two stacked `<canvas>` — main (series paths, redrawn on data/zoom) and highlight (crosshair/markers, cleared on each `mousemove`). DOM layer above for axis ticks, zoom-rect `<div>`, tooltip. Full-chart SVG rejected (layout cost ∝ point count).

**Draw scheduling**: RAF + dirty flag per chart; multiple state changes within one frame coalesce into one draw. Highlight canvas repaints synchronously on `mousemove` (exempt from coalescing).

**Path2D caching**: paths built in normalized [0,1]² coords. Cache key: `(seriesId, xMin, xMax, yMin, yMax, decimationBucketCount)` where `decimationBucketCount = nextPow2(pixelWidth)` (power-of-2 quantization improves hit rate on resize). Hit: draw via `ctx.setTransform()`. LRU, 200 entries/chart; evicted when `y` array reference changes.

**Data normalization** (one-time per series): scan `y` → `Uint8Array` flags → copy with boundary-substituted values → compute `yMin`/`yMax`. Normalized copy drives rendering; original retained for tooltips.

**DPR/Resize**: `devicePixelRatio` tracked via media query; canvas sized at CSS × DPR. `ResizeObserver` triggers attribute update + cache eviction + RAF redraw. Raster cap: effective DPR floored so `cssSize × DPR ≤ 4096`, applied per-axis independently.

**Virtualization**: `IntersectionObserver` — off-viewport charts skip redraws and release canvas backing (`canvas.width = 1`); data stays in memory. Full redraw on re-entry.

**Rejected**: WebGL (16-context browser cap; no native wide/dashed lines). OffscreenCanvas/Workers (structured-clone IPC latency measurable at 100k pts).

---

## Interaction

**Zoom**: X-only drag rectangle → writes `xRange` to controller (or local). Double-click resets to `null`. Scroll wheel ±10%/tick around cursor X.

**Pan**: Alt+drag or single-touch. No momentum. Pinch-zoom not supported.

**Crosshair**: `mousemove` → binary search on each series' own `x` → `highlightX` stored as raw data-coord X (unsnapped); each chart snaps independently. Tooltip lists all series values; NaN/±Inf show special labels.

**Keyboard**: `Escape` resets zoom; arrow keys pan 10%/press when chart focused.

---

## React API

```tsx
<Chart series={seriesArray} yScale="symlog" width={600} height={300} />

const ctrl = useSharedController({ initialXRange: [0, 1000] });
<Chart series={loss} controller={ctrl} />
<Chart series={gradNorm} controller={ctrl} yScale="log" />
```

`useSharedController` returns a stable ref; charts subscribe/unsubscribe on mount/unmount.

---

## API Surface

```ts
type ScaleType = 'linear' | 'log' | 'symlog';

interface Series { id: string; x: Float64Array; y: Float64Array;
  type: 'line'|'point'|'band-lo'|'band-hi'; bandId?: string;
  color: string; width?: number; }

interface HoveredPoint { seriesId: string; x: number;
  y: number | null; flags: 'nan'|'pos-inf'|'neg-inf'|null; }

interface ControllerState { xRange: [number,number]|null; highlightX: number|null; }

interface ChartProps { series: Series[]; xScale?: ScaleType; yScale?: ScaleType;
  ySymlogThreshold?: number; yRange?: [number,number];
  width?: number|'auto'; height?: number|'auto'; controller?: SharedController;
  onZoom?: (xRange: [number,number]) => void;
  onHover?: (x: number, points: HoveredPoint[]) => void; }

interface SharedController { subscribe(l: ()=>void): ()=>void;
  getSnapshot(): ControllerState; setXRange(r: [number,number]|null): void;
  setHighlightX(x: number|null): void; }

function useSharedController(opts?: { initialXRange?: [number,number] }): SharedController;
```

All types exported. No default export.

---

## Build

ESM-only; no CJS. Entry: `index.ts` → `dist/index.js` + `.d.ts`. Zero runtime deps; React peer `^18 || ^19`. Target ES2020. Bundler: Vite lib mode or tsup.

---

## Risks and Assumptions

- `x`/`y` must be `Float64Array`; `x` must be monotonically increasing and finite (binary search precondition; not validated at runtime).
- Memory risk: 100 charts × 1M pts × 2 arrays × 8 B ≈ 1.6 GB; caller must pre-aggregate to 100k.
- Path2D `setTransform()` reuse may produce sub-pixel rounding artifacts on some GPU/browser combos; negligible at normal line widths.
- 200-entry LRU may thrash under many series + high zoom frequency; mitigate by snapping to discrete zoom levels.

---

## Out of Scope

SSR, accessibility, plugins/theming/animations, bar/pie/categorical, CommonJS, multiple Y axes, Y-axis zoom, touch pinch-zoom, Y-axis cross-chart sync.
