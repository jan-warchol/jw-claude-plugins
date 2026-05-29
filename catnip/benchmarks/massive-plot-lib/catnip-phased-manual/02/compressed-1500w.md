# PlotLib: High-Performance Canvas Plotting Library — Spec

## Overview

PlotLib is an ESM-only, zero-dependency, React-peered canvas plotting library for ML training dashboards. It renders line, point, and band charts at scale — up to 100k points per chart, 1M per series (pre-aggregated server-side), across 100+ visible charts — without client-side decimation.

Performance targets: match uPlot render throughput; match Dygraphs interaction responsiveness.

---

## Chart Types

**Line**: polyline in series order; gaps at NaN; optional fill-to-zero for area charts.  
**Point**: scatter dots; configurable size; special markers for NaN/±Inf.  
**Band**: filled region between two paired series (e.g., min/max envelope, confidence interval). Paired series must share the same `Float64Array` reference for X; mismatched X produces incorrect rendering without a thrown error.  
Per-series `drawMode` supports `'line+point'` combinations.

---

## Data Model

```ts
type SeriesData = { id: string; x: Float64Array; y: Float64Array }
type ChartData  = { id: string; series: SeriesData[] }
```

- `id` must be stable across re-renders. Data changes require a new `Float64Array` reference; in-place mutation is not detected.
- `x` must be monotonically non-decreasing; PlotLib does not sort.
- Series with different `x` arrays are fully supported; no shared-X assumption.
- Callers are responsible for server-side aggregation. PlotLib never decimates.

### Normalization (one-time per series.id + array reference)

1. Validate `x.length === y.length`; scan for NaN/±Inf; record indices in `specialIndices`.
2. Compute `xMin/Max`, `yMin/Max`, `yP01/yP99` (ignoring specials).
3. Store x remapped to `[0,1]` (zoom-normalized, used by Path2D cache).

---

## Scales

| Y mode | Description |
|--------|-------------|
| `linear` | Default. |
| `symlog` | Linear threshold `C` auto-derived as `percentile(|y|, 5)` over non-zero finite values, or caller-supplied via `linearThreshold`. |
| `log` | Alias: symlog with `C` derived to avoid −∞ at zero. |

X: always linear, independent per series.

---

## Special Values and Outlier Marking

| Value | Line | Point |
|-------|------|-------|
| `NaN` | Gap | Hollow diamond |
| `+Inf` | Gap | Up-arrow at top edge |
| `−Inf` | Gap | Down-arrow at bottom edge |

Special markers render on the highlight canvas to avoid invalidating the main path cache.

**Outliers** (beyond `yP01`/`yP99`): rendered normally in all views; on hover, the highlight canvas draws a colored ring when the crosshair lands within 3px. No caller pre-labeling required. Thresholds computed per-series during normalization; no cross-series comparison.

---

## Canvas Architecture

```
┌─────────────────────────────┐
│  DOM overlay (z: 30)        │  ← axes/labels, crosshair divs, zoom-rect
│  Highlight canvas (z: 20)   │  ← hovered series, specials, outlier rings
│  Main canvas (z: 10)        │  ← all series Path2D (cached)
└─────────────────────────────┘
```

**Main canvas**: `Path2D` built in zoom-normalized coords (x,y ∈ [0,1]); replayed via `DOMMatrix`. Cache key: `(series.id, zoomLevel)`, quantized to 128 integer levels per decade — sub-level zooms reuse the path. LRU cap: 32 per chart. Invalidated on data change or level crossing.

**Highlight canvas**: cleared and redrawn on every pointer-move / `highlightX` update. Renders hovered series at 2× `lineWidth`, selected point markers, NaN/±Inf symbols, outlier rings, and crosshair dots. Separate canvas prevents main-canvas redraws during interaction.

**DOM overlay**: axes as `<span>` (subpixel text, no DPR math); crosshair and zoom-rect as `<div>` (crisp 1px borders). Axes re-laid-out via `requestAnimationFrame` after zoom.

---

## Interaction Model

**Zoom**: drag on plot area → zoom-rect `<div>` → on release, `setXDomain([x0, x1])`. Minimum drag 4 CSS pixels; narrower drags treated as clicks. Double-click resets to `null` (show all). X-only; Y auto-scales to the visible range. Without a controller, zoom is chart-local.

**Pan**: scroll wheel (deltaX or shift+deltaY) shifts domain by 15% of visible range per tick; throttled to one `setXDomain` per animation frame.

**Touch**: two-finger pinch zooms X domain; single-finger drag passes to page scroll.

**Hover**: pointer-move over any chart calls `setHighlightX(x)` in data space; each chart independently binary-searches its own x array and renders an intersection dot on the highlight canvas. Pointer-leave → `setHighlightX(null)`.

**onHover callback** (fires on all `highlightX` updates, including cross-chart; `null` on leave; one entry per series):
```ts
type HoverPoint = {
  seriesId: string; xIndex: number; x: number; y: number;
  isOutlier: boolean; isSpecial: boolean;
}
onHover?: (points: HoverPoint[] | null) => void
```

---

## DPR and Resize

- Canvas size: `Math.round(cssSize × devicePixelRatio)`; `ctx.scale(dpr, dpr)` once per resize.
- `ResizeObserver` on container, debounced to one frame.
- Raster cap 16384×16384; DPR silently reduced if exceeded. No error thrown; callers should avoid chart CSS widths > 8192px.
- DPR change (monitor switch) flushes canvas and Path2D cache.

---

## Shared Controller

Reactive-only: late-mounting charts read state synchronously, avoiding the "async blink storm" where charts briefly render at the wrong zoom before snapping to synced state.

```ts
type SharedController = {
  xDomain: Signal<[number, number] | null>  // null = show all
  highlightX: Signal<number | null>          // data-space X under cursor
  activeChartId: Signal<string | null>
  setXDomain(range: [number, number] | null): void
  setHighlightX(x: number | null): void
}
// Signal<T>: { get(): T; set(v: T): void; subscribe(fn): Unsubscribe }
// Minimal internal pub/sub — no external reactive library.
```

When `setXDomain` is called, all subscribed charts receive the new domain in the same microtask and schedule a repaint. When `xDomain` falls entirely outside a series' x range, the chart renders empty axes with no series paths. Y is never synced; each chart auto-scales its Y domain independently.

**Controller-less**: omit `controller` prop for chart-local zoom/highlight. Local and controller-driven charts may coexist on the same page.

---

## Viewport Virtualization

Single `IntersectionObserver` (threshold `0.0`) on all containers. Off-viewport: canvas collapsed to `1×1` (releases GPU texture memory); CSS height preserved — `display:none` is avoided because it removes elements from layout and causes scroll-jump in tall dashboard pages. On entry: dimensions restored, repaint scheduled next frame.

---

## React API

```tsx
import { Chart, useSharedController } from 'plotlib'
const ctrl = useSharedController()  // stable ref across re-renders

<Chart data={chartData} controller={ctrl} width="100%" height={300}
  yScale={{ mode: 'symlog' }}
  series={[{ id: 'loss', color: '#e74c3c', drawMode: 'line+point', lineWidth: 1.5 }]}
  onHover={(points) => void} />
```

Controlled component; signal updates bypass the React reconciler via direct `useEffect` subscriptions. `data` compared by reference; cache flushed only for series whose `id` or `Float64Array` reference changed.

```ts
type SeriesConfig = {
  id: string; color: string
  drawMode: 'line' | 'point' | 'band' | 'line+point'
  lineWidth?: number     // default 1
  pointRadius?: number   // default 3
  opacity?: number       // default 1
  bandPair?: string      // band mode: id of the paired series
}
```

---

## Performance Constraints

| | |
|-|-|
| Max pts/chart | 100k (100 series × 1k pts, or 1k series × 100 pts) |
| Max pts/series | 1M — aggregated by caller; never decimated |
| Visible charts | 100+ |
| WebGL | Rejected: 16-context limit; no native wide lines/dashes |
| OffscreenCanvas/Workers | Rejected: IPC cost exceeds savings at ≤100k pts |
| Deps | Zero runtime; React peer |
| Format | ESM only |

### Path2D Cache Budget

Bounded at 32 entries per chart (default; ~5 zoom decades × ~6 series), LRU eviction. At 100 visible charts, peak is ~3,200 cached Path2D objects; each proportional to visible-range point count after zoom quantization.

---

## Axes and Tick Generation

~6–8 X ticks from visible domain (round numbers preferred); time-formatted if all x > 1e9 (Unix timestamp heuristic). Y ticks warped through symlog transform. Labels: `Intl.NumberFormat` compact ("1.2M"). Optional horizontal grid lines at Y ticks drawn on main canvas before series paths.

---

## Design Rationale

**Two canvases + DOM overlay**: a single canvas would redraw all 100k-pt paths on every pointer-move — a multi-millisecond repaint. Splitting stable (main) from volatile (highlight) eliminates that cost. DOM axes give subpixel text rendering and crisp 1px lines for free, without per-DPR scaling arithmetic.

**Path2D in zoom-normalized coords**: data-coord paths must rebuild on every viewport change. Zoom-normalized paths survive viewport changes via a cheap matrix transform; 128-level/decade quantization bounds cache size with < 1px geometric error.

**Reactive-only controller**: an imperative init-sync approach requires all charts to have mounted before state is pushed — impossible to guarantee in async React renders. Reactive signals let each chart read current state on mount with no coordination, eliminating async blink storms.

---

## Assumptions, Risks, and Open Questions

**Assumptions**: x is sorted ascending (required for correct rendering and binary search); callers aggregate server-side appropriately; `id` strings are semantically stable across renders.

**Risks**:
- *Adversarial zoom*: rapid zoom builds a full 100k-pt path per level; LRU bounds retained objects but peak allocation during rapid zoom can spike.
- *IntersectionObserver batch*: on initial page load with 100+ charts, a large batch may fire, queuing many canvas inits in one frame. Mitigated by RAF-debounce on repaint scheduling.
- *Mobile DPR*: silent DPR reduction at the raster cap produces slightly blurry output with no developer warning.

**Open questions**:
- Should `onHover` fire only on local pointer-moves rather than all `highlightX` updates?
- Should a `yDomain` prop override auto-scaling (e.g., fix loss axis to [0, 1])?
- Is a `visible` per-series flag needed to hide/show series without removing them from `data`?

---

## Out of Scope

SSR, accessibility, plugins/theming/animation, bar/pie/categorical charts, CommonJS, client-side decimation, Y-axis synchronization.
