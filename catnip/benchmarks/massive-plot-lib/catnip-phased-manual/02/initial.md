# PlotLib: High-Performance Canvas Plotting Library — Spec

## Overview

PlotLib is an ESM-only, zero-dependency, React-peered canvas plotting library targeting ML training dashboards. It renders line, point, and band charts at massive scale — up to 100k points per chart, 1M points per series (pre-aggregated), across 100+ simultaneously visible charts — without client-side decimation.

Performance targets: match uPlot render throughput; match Dygraphs interaction responsiveness.

---

## Chart Types

### Line
Polyline connecting samples in series order. Gaps inserted at NaN values. Optional fill-to-zero for area charts.

### Point
Scatter dots per sample. Size configurable per series. Special marker shapes for NaN, +Inf, −Inf (see §Special Values).

### Band
Filled region between two series (e.g., min/max envelope, confidence interval). Upper and lower series share the same X array.

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
- `id` fields must be stable across re-renders for cache validity.
- Series with different `x` arrays are fully supported; no shared-X assumption.
- Callers are responsible for server-side aggregation. PlotLib never decimates.

### Data Normalization

On `SeriesData` ingestion, PlotLib runs a one-time normalization pass:

1. Validate lengths match.
2. Scan for NaN/±Inf, recording their indices in a separate `specialIndices` array.
3. Compute per-series `xMin`, `xMax`, `yMin`, `yMax` (ignoring specials).
4. Store a `zoom-normalized` copy of `x` mapped to `[0, 1]` range (used by Path2D cache).

Normalization result is keyed by `series.id`. If the same ID appears with identical `Float64Array` reference, normalization is skipped (cache hit).

---

## Scales

### Y-Axis Scale Modes

| Mode | Description |
|------|-------------|
| `linear` | Default. |
| `symlog` | Symmetric log scale with configurable linear threshold `C`. Log is a special case of symlog with `C → 0`. |

**Auto-derivation for symlog**: When `mode: 'symlog'` is requested without explicit `C`, PlotLib computes `C` from the data: `C = percentile(|y|, 5)` over non-zero, non-special values. Callers may override with an explicit `linearThreshold` parameter.

Log-only mode (`C = 0`) is exposed as `mode: 'log'`; internally it delegates to symlog with a derived small epsilon to avoid `-Infinity` at zero.

### X-Axis Scale

Always linear. Independent per series (no global X domain enforced).

---

## Special Values

NaN and ±Inf are first-class:

| Value | Line rendering | Point rendering |
|-------|---------------|-----------------|
| `NaN` | Gap (line break) | Hollow diamond marker |
| `+Inf` | Gap | Up-arrow triangle at top of plot area |
| `−Inf` | Gap | Down-arrow triangle at bottom of plot area |

Special markers are rendered on the highlight canvas (see §Canvas Architecture) to avoid invalidating the main path cache.

---

## Canvas Architecture

Each chart owns a stack of two `<canvas>` elements plus DOM overlays, all positioned `absolute` within a single container `<div>`:

```
┌─────────────────────────────┐
│  DOM overlay (z: 30)        │  ← crosshair, zoom-rect, axes, labels
│  Highlight canvas (z: 20)   │  ← hovered series, special markers, selection
│  Main canvas (z: 10)        │  ← all series paths (cached Path2D)
└─────────────────────────────┘
```

### Main Canvas

- Renders all series using cached `Path2D` objects.
- `Path2D` is built in **zoom-normalized coordinates** (x ∈ [0,1], y ∈ [0,1] within current viewport), then replayed with a `DOMMatrix` transform at paint time.
- Cache key: `(series.id, zoomLevel)` where `zoomLevel` is a quantized integer (128 levels per decade). Zooming within one level reuses the cached path, only the transform changes.
- Invalidated when: series data changes (by `id`), zoom crosses a level boundary.

### Highlight Canvas

- Cleared and redrawn on every pointer-move.
- Renders: hovered series (thicker stroke), selected point markers, NaN/±Inf symbols, crosshair intersection dots.
- Separate canvas prevents main-canvas redraws during interaction.

### DOM Overlay

- Axes (tick marks + labels): rendered as absolutely positioned `<span>` elements.
- Crosshair lines: `<div>` with `border` styling (avoids canvas for crisp 1px lines).
- Zoom-rect: semi-transparent `<div>`.

Axes are re-laid-out via `requestAnimationFrame` after zoom changes; label strings are formatted JS-side.

---

## DPR and Resize Handling

- Canvas `width`/`height` set to `Math.round(cssWidth * devicePixelRatio)`.
- `ctx.scale(dpr, dpr)` applied once after resize.
- `ResizeObserver` on the container triggers resize; debounced to one frame.
- Raster cap: canvas dimensions capped at `16384 × 16384` (WebGL/driver limit for raster surfaces). If a chart would exceed this at current DPR, DPR is reduced to fit.
- DPR changes (display movement) trigger full re-init of canvas dimensions and Path2D cache flush.

---

## Shared Controller

The shared controller synchronizes zoom, pan, and highlight across charts. It is **reactive-only**: it holds no mutable imperative state that is applied at construction time.

```ts
type SharedController = {
  // Signals (reactive state):
  xDomain: Signal<[number, number] | null>   // null = show all
  highlightX: Signal<number | null>           // data-space X under cursor
  activeChartId: Signal<string | null>

  // Methods:
  setXDomain(range: [number, number] | null): void
  setHighlightX(x: number | null): void
}
```

Charts subscribe to `xDomain` and `highlightX` signals. When a chart mounts after the controller is initialized, it reads current signal values synchronously — no async handshake, no init-sync flush required. This avoids the "async blink storm" where late-mounting charts briefly render at the wrong zoom before snapping to the synced state.

Signal implementation: minimal internal pub/sub (no external reactive library). `Signal<T>` is a simple `{ get(): T; set(v: T): void; subscribe(fn): unsubscribe }`.

### Synced Zoom

- Drag-to-zoom on any chart calls `controller.setXDomain(newRange)`.
- All subscribed charts receive the new domain in the same microtask and schedule a repaint.
- Double-click resets to `null` (full range).
- Y-axis is never synced (each chart has independent Y scale).

### Synced Highlight

- Pointer-move on any chart calls `controller.setHighlightX(x)` in data space.
- All charts render their crosshair at the nearest sample to `highlightX`.
- Pointer-leave calls `controller.setHighlightX(null)`.

---

## Viewport Virtualization

Charts outside the browser viewport are virtualized:

- A single `IntersectionObserver` watches all chart containers.
- Off-viewport charts: canvases are not painted; canvas `width`/`height` set to `1 × 1` to release GPU memory; container retains its CSS height (layout stable).
- On entering viewport: canvas dimensions restored, full repaint scheduled.
- Threshold: `0.0` (any pixel visible triggers activation).

This enables 100+ charts in a page without accumulating GPU canvas memory for all of them simultaneously.

---

## React API

```tsx
import { Chart, SharedController, useSharedController } from 'plotlib'

// Controller hook (stable reference across re-renders)
const ctrl = useSharedController()

<Chart
  data={chartData}           // ChartData
  controller={ctrl}          // optional
  width="100%"               // CSS value or number (px)
  height={300}
  yScale={{ mode: 'symlog' }}
  series={[
    { id: 'loss', color: '#e74c3c', drawMode: 'line+point', lineWidth: 1.5 },
    { id: 'val_loss', color: '#3498db', drawMode: 'line' },
  ]}
  onHover={(point) => void}  // optional
/>
```

- `Chart` is a controlled component. All state lives in `ChartData` and `SharedController`.
- Re-renders triggered by signal updates do not re-run the React reconciler for unrelated components; charts subscribe directly to signals.
- `data` identity is compared by reference; switching to a new `ChartData` object flushes caches for changed `series.id`s only (stable IDs preserved).

### SeriesConfig

```ts
type SeriesConfig = {
  id: string             // must match SeriesData.id
  color: string          // CSS color string
  drawMode: 'line' | 'point' | 'band' | 'line+point'
  lineWidth?: number     // default 1
  pointRadius?: number   // default 3
  opacity?: number       // default 1
  bandPair?: string      // for band mode: id of the paired series
}
```

---

## Performance Constraints and Invariants

| Constraint | Value |
|------------|-------|
| Max points per chart | 100k (100 series × 1k pts, or 1k series × 100 pts) |
| Max points per series (usable) | 1M (pre-aggregated by caller) |
| Max simultaneous visible charts | 100+ |
| Decimation | Never performed by PlotLib |
| WebGL | Rejected: browser 16-context limit, no native wide lines/dashes |
| OffscreenCanvas / Workers | Rejected: IPC serialization cost exceeds canvas savings at this point count |
| Dependencies | Zero runtime deps; React is a peer dependency |
| Module format | ESM only; no CommonJS output |

### Path2D Cache Budget

The Path2D cache is bounded: at most `maxCachedPaths` entries per chart (default 32, covering ~5 zoom decades × ~6 series). LRU eviction. Memory overhead per cached path is proportional to point count but bounded by zoom-level quantization (fewer points needed at higher zoom).

---

## Axes and Tick Generation

- X-axis ticks: generated from visible domain using a target of ~6–8 ticks, preferring round numbers. Time-formatting if x values look like Unix timestamps (heuristic: all values > 1e9).
- Y-axis ticks: same strategy; symlog scale warps tick positions through the symlog transform.
- Tick labels: formatted with `Intl.NumberFormat` (compact notation for large values, e.g. "1.2M").
- Grid lines: optional horizontal lines at Y ticks, drawn on main canvas before series paths.

---

## Out of Scope

The following are explicitly excluded from this library:

- **SSR / server-side rendering**: Canvas is browser-only. No Node.js or JSDOM support.
- **Accessibility**: No ARIA roles, keyboard navigation, or screen reader support.
- **Plugins / theming / animation**: No extension points, no transition animations, no theme tokens.
- **Bar, pie, categorical charts**: Only line, point, band.
- **CommonJS**: ESM-only. No `require()` support.
- **Client-side decimation**: Callers aggregate server-side; PlotLib renders what it receives.
- **Y-axis synchronization**: Each chart has its own Y domain.
