## Prompt

```
Write a spec for a fast, canvas-based plotting library -
line/point/band charts at massive scale.

Context: ML training dashboards, many charts × many series, ≤100k pts/chart
from 1M+/series pre-aggregated server-side. Hunt outliers; NaN/±Inf markers;
synced zoom+highlight; log/symlog; independent X per series. uPlot perf bar (no
decimation); Dygraphs responsiveness bar. Zero deps; React peer.

Bake in: 100k pts/chart (100×1000 or 1000×100), 1M usable, 100+ charts
loaded/visible; log = symlog special case, params auto-derived; stable ids as
cache keys; reactive-only shared controller (no init sync — async blink
storms); Path2D cached in zoom-normalized coords; data normalization; stacked
main+highlight canvases; DOM for crosshair/zoom-rect/axes; virtualize
off-viewport; DPR/ResizeObserver/raster-cap. Reject WebGL (16-context limit, no
wide lines/dashes) and OffscreenCanvas/Workers (IPC cost). Out of scope: SSR,
a11y, plugins/theming/animations, bar/pie/categorical, CommonJS. ESM-only.

Save it as a markdown file.
```

Model: sonnet 4.6 Effort: high

# Evaluation summary

| Topic              | spec-1 | spec-2 | spec-3 |
| ------------------ | ------ | ------ | ------ |
| Goal               | 3      | 3      | 3      |
| Requirements       | 3      | 3      | 3      |
| Solution           | 4      | 4      | 4      |
| Out of scope       | 3      | 3      | 3      |
| Uncertainty        | 4      | 3      | 3      |
| **Score (max 17)** | **17** | **16** | **16** |

| Metric      | spec-1 | spec-2 | spec-3 |
| ----------- | ------ | ------ | ------ |
| Word count  | 2 395  | 2 872  | 2 639  |
| Sections    | 18     | 17     | 13     |
| Subsections | 29     | 41     | 25     |

| Tier                   | spec-1  | spec-2   | spec-3  |
| ---------------------- | ------- | -------- | ------- |
| Must (out of 8)        | 5+ 1±   | 5+ 1± 1− | 4+ 3±   |
| Should (out of 16)     | 7+ 6±   | 5+ 7±    | 6+ 8±   |
| Could (out of 17)      | 3+      | 4+       | 4+      |
| Total points (145 max) | 90      | 77       | 92      |
| **Score**              | **62%** | **53%**  | **63%** |
