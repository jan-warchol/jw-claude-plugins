# PlotLib: High-Performance Canvas Plotting Library — Spec

## Overview

PlotLib is an ESM-only, zero-dependency, React-peered canvas plotting library for ML training dashboards. It renders line, point, and band charts at scale — up to 100k points per chart, 1M per series (pre-aggregated server-side), across 100+ visible charts — without client-side decimation.

Performance targets: match uPlot render throughput; match Dygraphs interaction responsiveness.

---

## Chart Types

**Line**: polyline in series order; gaps at NaN.  
**Point**: scatter dots; configurable size; special markers for NaN/±Inf.  
**Band**: filled region between two paired series. Paired series must share the same `Float64Array` reference for X; mismatched X produces incorrect rendering without a thrown error.

---

## Data Model

```ts
type SeriesData = { id: string; x: Float64Array; y: Float64Array }
type ChartData  = { id: string; series: SeriesData[] }
```

- `id` must be stable across re-renders. Data changes require a new `Float64Array` reference; in-place mutation is not detected.
- `x` must be monotonically non-decreasing; PlotLib does not sort.

### Normalization (one-time per series.id + array reference)

1. Validate `x.length === y.length`; scan for NaN/±Inf; record in `specialIndices`.
2. Compute `xMin/Max`, `yMin/Max`, `yP01/yP99` (ignoring specials); store x remapped to `[0,1]` for Path2D cache.

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

Special markers render on the highlight canvas, keeping the main path cache valid.

**Outliers** (beyond `yP01`/`yP99`): render normally; on hover a colored ring appears within 3px.

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

**Highlight canvas**: cleared and redrawn on every pointer-move / `highlightX` update.

**DOM overlay**: axes as `<span>` (subpixel text, no DPR math); crosshair and zoom-rect as `<div>` (crisp 1px borders). Axes re-laid-out via `requestAnimationFrame` after zoom.

---

## Interaction Model

**Zoom**: drag on plot area → zoom-rect `<div>` → on release, `setXDomain([x0, x1])`. Double-click resets to `null`. X-only; Y auto-scales.

**Pan**: scroll wheel shifts domain 15% per tick; throttled to one `setXDomain` per animation frame.

**Touch**: two-finger pinch zooms X domain; single-finger drag passes to page scroll.

**Hover**: pointer-move → `setHighlightX(x)` in data space; each chart binary-searches its own x array. Pointer-leave → `setHighlightX(null)`.

**onHover callback** (fires on all `highlightX` updates, including cross-chart; `null` on leave):
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
- `ResizeObserver` debounced to one frame.
- Raster cap 16384×16384; DPR silently reduced if exceeded.
- DPR change flushes canvas and Path2D cache.

---

## Shared Controller

Reactive-only: late-mounting charts read state synchronously, avoiding async blink storms.

```ts
type SharedController = {
  xDomain: Signal<[number, number] | null>
  highlightX: Signal<number | null>
  activeChartId: Signal<string | null>
  setXDomain(range: [number, number] | null): void
  setHighlightX(x: number | null): void
}
```

`Signal<T>`: minimal internal pub/sub. Omit `controller` for chart-local zoom; local and controller-driven charts may coexist.

---

## Viewport Virtualization

Single `IntersectionObserver` (threshold `0.0`). Off-viewport: canvas collapsed to `1×1` (releases GPU memory); CSS height preserved — `display:none` is avoided to prevent scroll-jump. On entry: dimensions restored, repaint scheduled.

---

## React API

```tsx
import { Chart, useSharedController } from 'plotlib'
const ctrl = useSharedController()

<Chart data={chartData} controller={ctrl} width="100%" height={300}
  yScale={{ mode: 'symlog' }}
  series={[{ id: 'loss', color: '#e74c3c', drawMode: 'line+point', lineWidth: 1.5 }]}
  onHover={(points) => void} />
```

Controlled component; signal updates bypass the React reconciler via `useEffect` subscriptions.

```ts
type SeriesConfig = {
  id: string; color: string
  drawMode: 'line' | 'point' | 'band' | 'line+point'
  lineWidth?: number; pointRadius?: number; opacity?: number
  bandPair?: string
}
```

---

## Performance Constraints

| | |
|-|-|
| Max pts/chart | 100k |
| Max pts/series | 1M — aggregated by caller; never decimated |
| Visible charts | 100+ |
| WebGL | Rejected: 16-context limit; no wide lines/dashes |
| OffscreenCanvas/Workers | Rejected: IPC cost exceeds savings at ≤100k pts |
| Deps | Zero runtime; React peer |
| Format | ESM only |

---

## Axes and Tick Generation

~6–8 X ticks (round preferred); time-formatted if x > 1e9. Y ticks warped through symlog transform. Labels: `Intl.NumberFormat` compact ("1.2M").

---

## Design Rationale

**Two canvases + DOM overlay**: a single canvas would redraw 100k-pt paths on every pointer-move. Splitting stable (main) from volatile (highlight) eliminates that cost. DOM axes give subpixel text and crisp 1px lines for free.

**Path2D in zoom-normalized coords**: paths survive viewport changes via a matrix transform; 128-level/decade quantization bounds cache size with < 1px geometric error. Reactive signals let late-mounting charts read state synchronously — imperative init-sync cannot be coordinated across async React renders.

---

## Assumptions, Risks, and Open Questions

**Assumptions**: x is sorted ascending; callers aggregate appropriately; `id` strings are semantically stable.

**Risk**: adversarial zoom builds a full 100k-pt path per level; LRU bounds retention but peak allocation can spike during rapid zoom.

**Open question**: should `onHover` fire only on local pointer-moves rather than all `highlightX` updates?

---

## Out of Scope

SSR, accessibility, plugins/theming/animation, bar/pie/categorical charts, CommonJS, client-side decimation, Y-axis synchronization.
