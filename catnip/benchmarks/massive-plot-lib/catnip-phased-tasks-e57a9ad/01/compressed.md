# Spec: Fast Canvas-Based Plotting Library for ML Dashboards

## Objective

Zero-dependency, ESM-only TypeScript charting library for ML training dashboards. Existing libraries sacrifice either performance (Dygraphs, Recharts) or React-friendliness (uPlot's imperative API). This targets ≤100k pts/chart with 100+ charts visible, pre-aggregated server-side data, uPlot-level render throughput, and Dygraphs-level interactivity.

Chart types: line, point (scatter), band (upper/lower ribbon). Ships as a React peer-dep component with a reactive shared controller for cross-chart zoom/highlight sync.

---

## Requirements

### Must do

- Render line, point, and band series on a 2D canvas
- ≤100k pts/chart primary target (100 series × 1000 pts or 1000 × 100); up to 1M pts with ≥2 fps interactivity
- Accept pre-aggregated server data — no client-side decimation
- 100+ charts simultaneously visible, viewport-virtualized
- NaN → gaps (pen-lift); ±Inf → edge markers at top/bottom of Y axis
- Outlier highlighting per series: IQR×1.5 default fence, overridable via `outlierFence` prop
- Synchronized X-domain zoom and crosshair across charts via shared controller; Y axes are chart-local (intentional — charts measure different quantities)
- Log and symlog scales on either axis; symlog threshold C auto-derived — no manual tuning
- Independent X axis per series; displayed X axis shows union of all series domains
- Stable string series IDs as Path2D cache keys
- Reactive-only controller: no imperative init-sync call (avoids async blink storms on mount)
- Two stacked canvases: main (data) + highlight (hover/selection), composited via `z-index`
- DOM layer (SVG) for axes, crosshair, zoom-rect
- DPR-aware: canvas backing store = display size × `devicePixelRatio`; re-render on DPR change
- ResizeObserver per chart; re-layout and re-render on resize
- Clamp canvas pixel dimensions to browser raster cap (detect at runtime; Safari: 4096 px)
- IntersectionObserver: skip render + release GPU memory for off-viewport charts; keep data and subscriptions alive
- Path2D cached in data-coordinate space; reused via `ctx.setTransform` across pan/zoom; invalidated on data or ID change
- Data normalization on ingest: sentinel NaN/±Inf in a parallel `Uint8Array`, sort by X if unsorted, compute statistics, tag outliers
- Per-series styling (color, line width, point radius, dash) as props

### Must not do

- WebGL (16-context limit; no native wide lines or dashes)
- OffscreenCanvas / Web Workers (IPC cost exceeds benefit)
- Client-side decimation
- CommonJS output; SSR; accessibility; animations; bar/pie/categorical; plugin or theming system

---

## Solution

### Package shape

ESM-only TypeScript; single entry `index.ts`. React `peerDependency` ≥18 (`useSyncExternalStore`). Exports: `<Chart>`, `createController()`, types. Build: Vite lib mode or tsup.

### Data format and `<Chart>` API

```ts
interface SeriesData {
  id: string              // stable cache key
  xs: Float64Array        // may be unsorted; may contain NaN/Inf
  ys: Float64Array        // same length as xs
  type: 'line' | 'point' | 'band-lower' | 'band-upper'
  bandId?: string         // pairs band-lower + band-upper with matching id
  color?: string          // default: built-in palette
  lineWidth?: number      // default 1.5
  pointRadius?: number    // default 3
  dash?: number[]         // default solid
  outlierFence?: number   // IQR multiplier; default 1.5; 0 = disable
  xScale?: 'linear' | 'log' | 'symlog'  // default 'linear'
  yScale?: 'linear' | 'log' | 'symlog'  // default 'linear'
}

interface ChartProps {
  series: SeriesData[]
  controller?: PlotController
  width?: number | string   // default '100%'
  height?: number | string  // default 300
  xLabel?: string
  yLabel?: string
}
```

`Float64Array` required (not `number[]`): avoids copy on normalization, eliminates GC pressure at 1M-pt scale. A band pairs one `band-lower` + one `band-upper` sharing `bandId`; each may have its own X array; upper < lower draws correctly with no clamping.

### Component architecture

```
<Chart>
  ├── <div container>      ← ResizeObserver + IntersectionObserver
  │   ├── <canvas main>    ← data paths; z-index 0
  │   ├── <canvas highlight> ← overlays; z-index 1
  │   └── <div dom-layer>  ← SVG axes, crosshair, zoom-rect; z-index 2
```

`position: absolute` stack in `position: relative` container. Highlight canvas is fully transparent except active overlays, so it repaints without touching the main canvas.

### Rendering pipeline

1. **Ingest** (keyed by series ID): scan for NaN/±Inf → sentinel `Uint8Array`; sort by X if needed; compute min/max/p5/p95/IQR; tag outliers in a `Set<number>`; memoize by ID + array reference.

2. **Coordinate transform**: linear/log → `ctx.setTransform(sx, 0, 0, sy, tx, ty)` computed per frame from viewport; symlog → project each point individually during Path2D construction (no affine form).

3. **Path2D construction** (linear/log: invalidated by data change; symlog: also by viewport change):
   - Line: `moveTo`/`lineTo` valid points; lift at NaN; ⊥/⊤ markers at ±Inf sentinels
   - Point: `rect(x-r, y-r, 2r, 2r)` squares (not arcs — stays undistorted under non-uniform setTransform)
   - Band: upper path forward + lower path backward + close → one filled `Path2D`
   - Outliers: separate `Path2D` per series, drawn last with accent color

4. **Frame render** (single global RAF scheduler; charts register/deregister):
   - Per visible chart: `setTransform` → `clearRect` → `stroke`/`fill`
   - Highlight canvas: repainted on pointer events only, not every tick

5. **DOM layer**: ticks via Wilkinson-style algorithm → SVG `<line>`+`<text>`; crosshair `<div>` snaps to nearest data X; zoom-rect `<div>` shown during drag.

### Interaction model

| Gesture | Action |
|---------|--------|
| `pointermove` | `setHighlightedX(dataX)` → all charts move crosshair |
| `pointerdown` + drag | draw zoom rect → `pointerup` → `setXDomain(range)` |
| `wheel` | zoom centered on cursor → `setXDomain(range)` |
| double-click / Escape | `reset()` to full data extent |

No click-drag-pan (conflicts with zoom-rect); users re-drag to adjacent regions instead.

### Scale types

- **Linear**: affine map
- **Log**: `Math.log10(x)`; throws if data contains ≤0
- **Symlog**: `sign(x) · log10(1 + |x|/C)`, normalized; C = smallest non-zero `|x|` clamped to `[1e-9, 1]`; log is a separate code path, not a degenerate symlog

### Shared controller

```ts
interface PlotController {
  xDomain: [number, number]
  highlightedX: number | null
  selectedSeries: Set<string>
  setXDomain(range: [number, number]): void
  setHighlightedX(x: number | null): void
  toggleSeries(id: string): void
  reset(): void
}
```

Plain reactive store (JS `Set` of listeners); `<Chart>` subscribes via `useSyncExternalStore`. Created outside the React tree and passed as a prop. Y-axis domain not in controller — each chart owns its Y range independently.

### Viewport virtualization

`IntersectionObserver` per chart. At `intersectionRatio === 0`: deregister from RAF scheduler, set canvas `width = 1` (releases GPU raster memory). On re-entry: re-register, restore dimensions, trigger one render. Data, Path2D cache, and subscriptions survive throughout.

### Performance targets

| Metric | Target |
|--------|--------|
| 100k pts, 1 chart, initial render | ≤ 16 ms |
| Pan/zoom (setTransform, linear) | ≤ 4 ms |
| 100 charts × 1k pts, first paint | ≤ 200 ms |
| 1M pts, 1 chart, initial render | ≤ 500 ms |
| Path2D memory | O(points), not O(zoom levels) |

---

## Alternative Solutions Considered

**WebGL**: 16-context browser limit; no native wide/dashed lines. **OffscreenCanvas + Workers**: `postMessage` costs ~2–5 ms/frame even with transferables — exceeds pan/zoom budget. **uPlot**: matches perf but imperative non-React API; no independent per-series X; no controller abstraction. **Dygraphs**: React-friendly but degrades above ~10k pts; no Path2D caching.

---

## Out of Scope

SSR; accessibility; plugins/theming; animations; bar/pie/categorical; client-side decimation; CommonJS; mobile touch gestures; Y-axis synchronization.

---

## Uncertainty

1. **Point squares vs circles**: Squares avoid distortion under non-uniform `setTransform` but differ from convention. Needs prototype to confirm visual acceptability.

2. **Symlog C at zero-heavy data**: Smallest non-zero `|x|` misbehaves if nearly all values are zero with one outlier. Fallback: if >90% zeros, treat axis as linear.

3. **Path2D memory at 100+ charts**: Rough estimate ~10 MB/chart × 100 = 1 GB. An LRU eviction cap (~50 MB) likely required; exact threshold from profiling.

4. **Union X axis with non-overlapping series**: May confuse users. Per-series axis lanes would fix it but complicate layout significantly. Accepted as known UX limitation.

5. **Global RAF singleton in micro-frontends**: Module-level singleton breaks when multiple library instances load on one page. Assumption: single instance per page.

6. **Symlog + pan/zoom performance**: Symlog paths rebuild on every viewport change. If symlog Y is common, this is a performance cliff. Mitigation (caching last N viewports) deferred to profiling.
