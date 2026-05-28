# PlotLib: High-Performance Canvas Plotting Library — Spec

## Overview

PlotLib is an ESM-only, zero-dependency, React-peered canvas plotting library targeting ML training dashboards. It renders line, point, and band charts at massive scale — up to 100k points per chart, 1M points per series (pre-aggregated server-side), across 100+ simultaneously visible charts — without client-side decimation.

Performance targets: match uPlot render throughput (no decimation path); match Dygraphs interaction responsiveness (crosshair and zoom feel instantaneous at 100k pts).

---

## Chart Types

### Line
Polyline connecting samples in series order. Gaps inserted at NaN values. Optional fill-to-zero for area charts.

### Point
Scatter dots per sample. Size configurable per series. Special marker shapes for NaN, +Inf, −Inf (see §Special Values).

### Band
Filled region between two series (e.g., min/max envelope, confidence interval). Upper and lower series must share the **same X array** (identical `Float64Array` reference or identical values); mismatched X arrays on band pairs are a usage error and will render incorrectly without a guarantee of a thrown exception.

Combination charts (line + points on same series) supported via per-series `drawMode` flags.

---

## Data Model

```ts
type SeriesData = {
  id: string          // stable string, used as cache key
  x: Float64Array     // may differ across series (independent X)
  y: Float64Array     // same length as x; NaN/±Inf allowed
}

type ChartData = {
  id: string
  series: SeriesData[]
}
```

- `x` and `y` must be `Float64Array` (typed arrays required; no JS number arrays).
- `id` fields must be stable across re-renders for cache validity. If a series `id` is reused with different data, callers must supply a new `Float64Array` reference (not mutate in place); PlotLib uses array reference equality to detect data changes.
- `x` values within a series must be **monotonically non-decreasing**. PlotLib does not sort; out-of-order x produces incorrect line rendering with no error.
- Series with different `x` arrays are fully supported; no shared-X assumption.
- Callers are responsible for server-side aggregation. PlotLib never decimates.

### Data Normalization

On `SeriesData` ingestion, PlotLib runs a one-time normalization pass:

1. Validate lengths match.
2. Scan for NaN/±Inf, recording their indices in a separate `specialIndices` array.
3. Compute per-series `xMin`, `xMax`, `yMin`, `yMax` (ignoring specials). Also record `yP99` and `yP01` (1st/99th percentile of finite values) for outlier marking.
4. Store a zoom-normalized copy of `x` mapped to `[0, 1]` range (used by Path2D cache).

Normalization result is keyed by `series.id`. If the same ID appears with identical `Float64Array` reference, normalization is skipped (cache hit).

---

## Scales

### Y-Axis Scale Modes

| Mode | Description |
|------|-------------|
| `linear` | Default. |
| `symlog` | Symmetric log scale with configurable linear threshold `C`. Log is a special case of symlog with `C → 0`. |

**Auto-derivation for symlog**: When `mode: 'symlog'` is requested without explicit `C`, PlotLib computes `C = percentile(|y|, 5)` over non-zero, non-special finite values. Callers may override with an explicit `linearThreshold` parameter.

Log-only mode is exposed as `mode: 'log'`; internally it delegates to symlog with a derived small epsilon to avoid `-Infinity` at zero.

### X-Axis Scale

Always linear. Independent per series (no global X domain enforced).

---

## Special Values and Outlier Marking

### NaN and ±Inf

| Value | Line rendering | Point rendering |
|-------|---------------|-----------------|
| `NaN` | Gap (line break) | Hollow diamond marker |
| `+Inf` | Gap | Up-arrow triangle at top of plot area |
| `−Inf` | Gap | Down-arrow triangle at bottom of plot area |

Special markers are rendered on the highlight canvas (see §Canvas Architecture) to avoid invalidating the main path cache.

### Outlier Marking

Points beyond the 1st/99th percentile of a series' finite values are considered outliers. In the default view they render normally (no clipping); the outlier threshold is used only to drive **visual emphasis on hover**: when the crosshair lands within 3 pixels of an outlier point, the highlight canvas draws a colored ring around it. This supports the ML use case of hunting anomalous loss spikes or gradient explosions without requiring the caller to pre-label outliers.

Outlier thresholds are computed per-series during normalization. No cross-series comparison is performed.

---

## Canvas Architecture

Each chart owns a stack of two `<canvas>` elements plus DOM overlays, all positioned `absolute` within a single container `<div>`:

```
┌─────────────────────────────┐
│  DOM overlay (z: 30)        │  ← crosshair, zoom-rect, axes, labels
│  Highlight canvas (z: 20)   │  ← hovered series, special markers, outlier rings
│  Main canvas (z: 10)        │  ← all series paths (cached Path2D)
└─────────────────────────────┘
```

### Main Canvas

- Renders all series using cached `Path2D` objects.
- `Path2D` is built in **zoom-normalized coordinates** (x ∈ [0,1], y ∈ [0,1] within current viewport), then replayed with a `DOMMatrix` transform at paint time.
- Cache key: `(series.id, zoomLevel)` where `zoomLevel` is a quantized integer (128 levels per decade). Zooming within one level reuses the cached path; only the transform changes.
- Invalidated when: series data changes (by `id`), or zoom crosses a level boundary.

### Highlight Canvas

- Cleared and redrawn on every pointer-move and on every `highlightX` signal update.
- Renders: hovered series (thicker stroke, 2× `lineWidth`), selected point markers, NaN/±Inf symbols, outlier rings, crosshair intersection dots.
- Separate canvas prevents main-canvas redraws during interaction.

### DOM Overlay

- Axes (tick marks + labels): rendered as absolutely positioned `<span>` elements. DOM is used rather than canvas so that tick labels benefit from browser subpixel text rendering and remain crisp at any DPR without manual scaling arithmetic.
- Crosshair lines: `<div>` with `border` styling (avoids canvas for crisp 1px lines at any DPR).
- Zoom-rect: semi-transparent `<div>`.

Axes are re-laid-out via `requestAnimationFrame` after zoom changes; label strings are formatted JS-side.

---

## Interaction Model

### Zoom

- **Drag (pointer down → move → up)** on the plot area draws a zoom-rect overlay `<div>`, then on release calls `controller.setXDomain([x0, x1])`. Without a controller, zoom is chart-local.
- Minimum drag width is 4 CSS pixels; narrower drags are treated as clicks and ignored.
- **Double-click** resets zoom to `null` (show all data).
- Zoom is **X-only**; Y auto-scales to the visible X range.

### Pan

- **Scroll wheel (deltaX or shift+deltaY)** pans the current X domain left/right by a fraction of the visible range per wheel tick (default 15%). Updates `controller.setXDomain` on each wheel event, throttled to one update per animation frame.

### Touch

- Two-finger pinch on the plot area zooms X domain. Single-finger drag is reserved for page scroll and does not interact with the chart.

### Hover / Crosshair

- Pointer-move over any chart sets `controller.setHighlightX(x)` in data space. Each chart independently finds the nearest sample per series (binary search on its own x array) and renders a dot on the highlight canvas.
- Pointer-leave sets `controller.setHighlightX(null)`, clearing all crosshairs.

### onHover Callback

```ts
type HoverPoint = {
  seriesId: string
  xIndex: number       // index into SeriesData.x
  x: number
  y: number            // raw value (may be NaN/±Inf)
  isOutlier: boolean
  isSpecial: boolean   // true if NaN or ±Inf
}

onHover?: (points: HoverPoint[] | null) => void
// null when pointer leaves
// one entry per series for the nearest sample to highlightX
```

---

## DPR and Resize Handling

- Canvas `width`/`height` set to `Math.round(cssWidth * devicePixelRatio)`.
- `ctx.scale(dpr, dpr)` applied once after resize.
- `ResizeObserver` on the container triggers resize; debounced to one animation frame.
- Raster cap: canvas dimensions capped at `16384 × 16384`. If a chart would exceed this at current DPR (possible on high-DPR mobile screens), DPR is silently reduced to fit. No error is thrown; callers should avoid chart CSS widths > 8192px.
- DPR changes (display movement between monitors) trigger full re-init of canvas dimensions and Path2D cache flush.

---

## Shared Controller

The shared controller synchronizes zoom, pan, and highlight across charts. It is **reactive-only**: it holds no mutable state applied at construction time.

```ts
type SharedController = {
  xDomain: Signal<[number, number] | null>   // null = show all
  highlightX: Signal<number | null>           // data-space X under cursor
  activeChartId: Signal<string | null>

  setXDomain(range: [number, number] | null): void
  setHighlightX(x: number | null): void
}
```

Charts subscribe to `xDomain` and `highlightX` signals. When a chart mounts after the controller is initialized, it reads current signal values **synchronously** — no async handshake. This avoids the "async blink storm" where late-mounting charts briefly render at the wrong zoom before snapping to the synced state.

Signal implementation: minimal internal pub/sub (no external reactive library). `Signal<T>` is `{ get(): T; set(v: T): void; subscribe(fn): Unsubscribe }`.

### Controller-less Operation

When no `controller` prop is passed, the chart manages zoom and highlight locally. Local zoom state is not shared. Local and controller-driven charts can coexist on the same page.

### Synced Zoom

- Drag-to-zoom on any chart calls `controller.setXDomain(newRange)`.
- All subscribed charts receive the new domain in the same microtask and schedule a repaint.
- When `xDomain` falls entirely outside a series' x range, the chart renders empty axes with no series paths.
- Y-axis is never synced (each chart auto-scales to visible Y independently).

### Synced Highlight

- Pointer-move on any chart calls `controller.setHighlightX(x)` in data space.
- Each chart independently finds the nearest sample via binary search on its own x array.
- Pointer-leave calls `controller.setHighlightX(null)`.

---

## Viewport Virtualization

- A single `IntersectionObserver` watches all chart containers (threshold `0.0`).
- Off-viewport charts: canvases set to `1 × 1` (releases GPU texture memory); container retains its CSS height (layout stable, no scroll-jump).
- On entering viewport: canvas dimensions restored, full repaint scheduled in the next animation frame.
- `display: none` is deliberately avoided; it removes the element from layout and causes scroll-jump in tall dashboard pages.

This enables 100+ charts without accumulating GPU canvas memory for all simultaneously.

---

## React API

```tsx
import { Chart, useSharedController } from 'plotlib'

const ctrl = useSharedController()   // stable reference across re-renders

<Chart
  data={chartData}           // ChartData
  controller={ctrl}          // optional; omit for local zoom
  width="100%"               // CSS value or number (px)
  height={300}
  yScale={{ mode: 'symlog' }}
  series={[
    { id: 'loss', color: '#e74c3c', drawMode: 'line+point', lineWidth: 1.5 },
    { id: 'val_loss', color: '#3498db', drawMode: 'line' },
  ]}
  onHover={(points) => void} // optional; see §Interaction Model
/>
```

- `Chart` is a controlled component. All state lives in `ChartData` and `SharedController`.
- Signal updates do not re-run the React reconciler for unrelated components; charts subscribe to signals directly inside `useEffect`.
- `data` identity compared by reference; only series whose `id` changed or whose `Float64Array` reference changed get their normalization cache flushed.

### SeriesConfig

```ts
type SeriesConfig = {
  id: string
  color: string
  drawMode: 'line' | 'point' | 'band' | 'line+point'
  lineWidth?: number     // default 1
  pointRadius?: number   // default 3
  opacity?: number       // default 1
  bandPair?: string      // for band: id of the paired lower/upper series
}
```

---

## Performance Constraints and Invariants

| Constraint | Value |
|------------|-------|
| Max points per chart | 100k (100 series × 1k pts, or 1k series × 100 pts) |
| Max points per series (usable) | 1M (pre-aggregated by caller) |
| Max simultaneous visible charts | 100+ |
| Decimation | Never |
| WebGL | Rejected: 16-context browser limit; no native wide lines or dashes |
| OffscreenCanvas / Workers | Rejected: IPC serialization cost outweighs canvas savings at ≤100k pts |
| Dependencies | Zero runtime deps; React is a peer dependency |
| Module format | ESM only |

### Path2D Cache Budget

Bounded at `maxCachedPaths` entries per chart (default 32, ~5 zoom decades × ~6 series). LRU eviction. At 100k pts and 32 cached paths per chart with 100 visible charts, peak cache size is ~3,200 Path2D objects; each is proportional to visible-range point count after zoom quantization.

---

## Axes and Tick Generation

- X-axis ticks: ~6–8 ticks from visible domain, preferring round numbers. Time-formatted if all x values > 1e9 (Unix timestamp heuristic).
- Y-axis ticks: same strategy; symlog scale warps tick positions through the symlog transform before layout.
- Tick labels: `Intl.NumberFormat` with compact notation (e.g., "1.2M").
- Grid lines: optional horizontal lines at Y ticks, drawn on main canvas before series paths.

---

## Design Rationale

**Two canvases instead of one**: A single canvas would require clearing and redrawing all series on every pointer-move. At 100k pts, that is a multi-millisecond repaint. Splitting main (stable) and highlight (volatile) canvases eliminates that cost — the main canvas only repaints on zoom or data change.

**Path2D in zoom-normalized coords**: Building paths in data coords means a path must be rebuilt whenever the viewport changes. Zoom-normalized coords (x ∈ [0,1] in current viewport) allow the same path to be replayed with a cheap matrix transform for sub-level zooms. The quantization to 128 levels per decade bounds the number of distinct paths while keeping geometric error below 1 screen pixel.

**DOM for axes, not canvas**: Canvas text requires manual DPR scaling and lacks subpixel rendering. DOM `<span>` elements get browser subpixel text rendering for free and are easier to position precisely using CSS absolute layout.

**Reactive-only controller**: An imperative init-sync approach (call `.syncState()` on mount) would require all charts to have mounted before state is pushed, which is impossible to guarantee in async React renders. Reactive signals let each chart read current state on mount without coordination.

---

## Assumptions, Risks, and Open Questions

**Assumptions**:
- X values within each series are monotonically non-decreasing (required for correct rendering and binary search on highlight).
- Callers perform server-side aggregation appropriate to the visible range; PlotLib has no way to validate aggregation quality.
- Stable `id` strings are the caller's responsibility; PlotLib cannot detect accidental ID reuse across semantically different series.

**Risks**:
- **Memory at adversarial zoom**: If a user zooms to a very fine range, each zoom level builds a path with all 100k points visible in that range. The LRU cap of 32 per chart bounds retained objects, but peak allocation during rapid zoom can be high.
- **IntersectionObserver batch scaling**: On initial page load with 100+ charts, the IntersectionObserver may fire a large batch. Each callback schedules a repaint; if all fire in the same frame, 100 canvas inits may be queued. This is mitigated by the single-RAF-debounce on repaint scheduling.
- **Mobile DPR + large charts**: On a device with DPR=3 and a 600px-wide chart, canvas physical width is 1800px — well under the cap. But if chart CSS width is set to `100vw` on a tablet in landscape, the cap reduction may produce slightly blurry output without a warning to the developer.

**Open questions**:
- Should `onHover` fire on every `highlightX` signal update (even when triggered by another chart), or only on local pointer-moves? Current spec fires on all updates.
- Should there be a `yDomain` prop to override auto-scaling (e.g., fix loss to [0, 1])? Currently out of scope but commonly needed.
- Is a `visible` per-series flag needed to hide/show individual series without removing them from `data`?

---

## Out of Scope

- **SSR / server-side rendering**: Canvas is browser-only.
- **Accessibility**: No ARIA, keyboard navigation, or screen reader support.
- **Plugins / theming / animation**: No extension points, no transition animations, no theme tokens.
- **Bar, pie, categorical charts**: Only line, point, band.
- **CommonJS**: ESM-only.
- **Client-side decimation**: Callers aggregate server-side.
- **Y-axis synchronization**: Each chart auto-scales independently.
