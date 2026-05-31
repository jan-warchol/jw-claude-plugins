# Canvas Plotting Library — Spec

## Objective

Zero-dependency, ESM-only, canvas-based charting library for ML training dashboards. Renders line/point/band charts over pre-aggregated datasets (≤100k pts/chart from 1M+/series server-side). Supports synchronized zoom/pan across 100+ simultaneous charts, outlier hunting, NaN/±Inf markers, log/symlog scales, independent X per series. React peer dep only.

**Performance bar:** initial render ≥ uPlot (no client decimation); zoom/pan ≥ Dygraphs (60fps, no jank); 100+ visible charts without cascading re-renders.

---

## Requirements

### Must do

- **Chart types**: line, point, band (filled area between two series) on HTML Canvas.
- **Scale**: ≤100k pts/chart (e.g. 100 series × 1k pts); 1M pts soft limit.
- **Concurrency**: 100+ charts loaded and visible simultaneously.
- **Synced zoom/highlight**: shared reactive controller; no init-time sync (avoids async blink storms).
- **Interaction**: scroll-wheel zoom; drag-to-pan; shift-drag zoom-rect; double-click reset.
- **Scales**: linear, log, symlog; log is symlog with threshold → 0; threshold auto-derived from data.
- **Independent X per series**: each series has its own x-array; all series share one chart-level x-domain and one y-domain.
- **NaN/±Inf markers**: gap+dot for NaN; capped arrows for ±Inf.
- **Outlier hunting**: per-series color/glyph emphasis beyond N·σ (σ from finite values); `onOutliersFound` callback.
- **Viewport virtualization**: IntersectionObserver; off-viewport charts skip render, release highlight canvas.
- **DPR + raster cap**: canvas sized to `logical × dpr`; capped at ~16 384 px max dimension.
- **ResizeObserver**: reflow and redraw on layout change.
- **React integration**: `<Chart>` + controller context; zoom/highlight bypass React state entirely.
- **ESM-only** publish.

### Must not do

- WebGL (~16-context browser limit; no native wide/dashed lines).
- OffscreenCanvas / Web Workers (IPC cost outweighs benefit).
- Client-side decimation (server pre-aggregates; render faithfully).
- Bundle React (peer dep).
- CommonJS build.

---

## Solution

### Canvas layer stack

Three stacked layers per chart:

| Layer | Type | Purpose |
|-------|------|---------|
| `main` | `<canvas>` | Series geometry; redrawn only on data/zoom change |
| `highlight` | `<canvas>` | Hover/selection overlay; cleared at pointer-event rate |
| `dom` | `<div>` | Axis tick labels, crosshair, zoom-rect, tooltip anchor |

Axes use the DOM layer because DOM text scales correctly with DPR; canvas text requires manual size adjustments and renders poorly at high DPR. The `highlight` canvas is detached (`width=0`) for off-viewport charts; `main` is preserved for instant re-entry.

### Render scheduling

Renders gate through one `requestAnimationFrame` per chart. A dirty flag is set on data/zoom/size change; the rAF callback clears it, then `clearRect` + re-applies transform + `stroke`/`fill` all series. Rapid events coalesce: only controller state at rAF fire time is used. No rAF queued when no chart is dirty.

### Path2D caching

Paths are built in **zoom-normalized coords**: x, y ∈ [0, 1] over the chart's full domain/range. Key: `(seriesId, dataVersion)`. At render time a single transform maps [0,1]² → pixels:

```
scaleX = canvasWidth / (zoomXMax - zoomXMin)
translateX = -zoomXMin * scaleX
scaleY = canvasHeight / (yMax - yMin)   // y-axis inverted
```

Zoom/pan never invalidates. Off-viewport charts evict Path2D entries after 30 s idle; `Float64Array` data is never evicted (caller manages lifetime).

### Chart type rendering

- **Line**: `moveTo`/`lineTo` Path2D, stroked through transform; NaN positions get `moveTo` gaps.
- **Point**: `arc()` is too slow at 100k pts (~1ms/1k). Use pixel-stamp (`ImageData` tile) for radius ≤ 1.5 px; Path2D of `rect(x-r, y-r, 2r, 2r)` for larger markers.
- **Band**: fill path = y forward + y2 reversed + `closePath()`; top/bottom edges stroked separately for independent styling.

### Shared controller

```ts
interface ChartController {
  zoom: { xMin: number; xMax: number };  // normalized [0,1]
  highlight: { x: number } | null;
  subscribe(cb: () => void): () => void;
  setZoom(zoom: Zoom): void;
  setHighlight(x: number | null): void;
}
```

Subscribers fire synchronously in the same microtask — no blink storm from async React batching. Charts read current state on mount; they never call `setZoom`/`setHighlight` during init (avoids cascade across 100+ concurrent mounts). Stable string IDs required as cache keys.

### Scale system

```ts
type Scale =
  | { kind: "linear" }
  | { kind: "log"; base?: 10 | Math.E }
  | { kind: "symlog"; threshold?: number }  // auto-derived if omitted
```

Symlog: `sign(x) × log(1 + |x|/C)`. Auto-derived `C = max(|data|) / 1000` (3 decades of linear near zero). `log` is symlog with C → 0.

### Series type and domain

```ts
interface Series {
  id: string;
  x: Float64Array;          // monotone increasing
  y: Float64Array;          // may contain NaN/±Inf
  kind: "line" | "point" | "band";
  bandY2?: Float64Array;
  outlierThreshold?: number; // σ units; omit to disable
}
```

Chart x-domain = union of series x-extents (or explicit `xDomain`). Chart y-domain = union of finite y-extents (or explicit `yDomain`). Same array reference may be shared across series.

### Axis ticks

Positions computed in data coords, projected via zoom transform. Linear: nice-interval algorithm (1/2/5 × 10^n). Log: powers of base. Symlog: linear ticks near zero + log ticks in log region. Labels are `<span>` elements in a fixed-size recycled pool; zoom updates only `left`/`top` CSS — no DOM insertion.

### NaN/±Inf markers

y-array scanned before Path2D build; indices stored in `Uint32Array`. NaN → `moveTo` gap + hollow circle at midline x. ±Inf → capped arrow at plot top/bottom. Drawn post-stroke in a separate pass, unaffected by transform.

### Data normalization

On `setSeries`: coerce to `Float64Array`; compute per-series extents (finite only); record special-value indices; increment `dataVersion`.

### Viewport virtualization

One shared `IntersectionObserver` per page. Enter: re-attach `highlight` canvas, schedule render. Leave: detach `highlight` canvas, start 30 s Path2D eviction timer.

### React integration

```tsx
const ctrl = createChartController();
<ChartControllerProvider value={ctrl}>
  <Chart id="loss" series={series} yScale={{ kind: "symlog" }} height={200} />
</ChartControllerProvider>
```

`useEffect` mounts engine and subscribes to controller. Zoom/highlight write directly to canvas, bypassing React state. Only structural prop changes (data, scale, size) cause React re-renders.

### DPR / raster cap

```ts
const dpr = Math.min(devicePixelRatio ?? 1, 3);
const CAP = 16384;
canvas.width  = Math.min(Math.round(cssW * dpr), CAP);
canvas.height = Math.min(Math.round(cssH * dpr), CAP);
```

---

## Alternative Solutions Considered

- **WebGL**: ~16-context limit makes 100+ charts impossible; no native wide/dashed lines.
- **OffscreenCanvas + Workers**: postMessage IPC cost at 100+ charts exceeds rendering savings; Path2D caching removes the main bottleneck anyway.
- **SVG**: 100k-point polyline in DOM is unusably slow; 100 such charts would freeze the page.
- **Client decimation**: would silently drop the outliers this tool exists to find.
- **State library for controller**: violates zero-deps; subscriber-set observable is sufficient.

---

## Out of Scope

SSR; a11y; plugin/theme/animation system; bar/pie/categorical charts; CommonJS/UMD; data fetching / live streaming; legend component; PNG/SVG export; per-series independent y-axes.

---

## Uncertainty

1. **React floor**: assumed React 18+ (`useSyncExternalStore`). React 16/17 needs a different subscription hook.
2. **Independent X semantics**: assumed = no shared x-array required, but still one x-domain per chart. Truly disjoint ranges would require rethinking zoom normalization.
3. **Outlier UX**: σ-threshold + visual marker assumed. Interactive selection (lasso, click-to-inspect) would need API expansion.
4. **Tooltip scope**: minimal crosshair + nearest-point readout assumed in scope; rich multi-series panel is not.
5. **Symlog heuristic**: `C = max(|data|) / 1000` may need per-series tuning for widely varying magnitudes.
6. **Raster cap**: 16 384 px is conservative (Chrome allows 65 536 px). Runtime detection via probe allocation may be better than a hardcoded constant.
7. **React bypass**: direct canvas writes for zoom/highlight are incompatible with Suspense/transitions; revisit if host app needs that coordination.
8. **Memory at scale**: 100 charts × 100 series × 1k pts × 8 B ≈ 80 MB (fine). At 1M pts/series budget rises sharply; callers own data lifetime — the library does not evict raw arrays.
9. **Edge cases**: `length === 0` or `length === 1` series should skip render and be no-ops for extent computation.
