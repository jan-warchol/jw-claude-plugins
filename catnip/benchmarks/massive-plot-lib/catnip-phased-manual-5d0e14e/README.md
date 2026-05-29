### Prompts

```
/catnip:draft-spec fast, canvas-based plotting library -
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
```

`/catnip:enrich-spec initial.md`

`/catnip:compress-spec enriched.md`

- Model: sonnet 4.6
- Effort: high
- Compression: word limit hardcoded to 1000

## Evaluation summary

| Topic              | run1-c1000 | run2-c1000 | run3-c1000 |
| ------------------ | ---------- | ---------- | ---------- |
| Goal               | 3          | 3          | 3          |
| Requirements       | 3          | 3          | 3          |
| Solution           | 4          | 4          | 4          |
| Out of scope       | 3          | 3          | 3          |
| Uncertainty        | 4          | 4          | 3          |
| **Total (max 17)** | **17**     | **17**     | **16**     |

| Metric      | run1-c1000 | run2-c1000 | run3-c1000 |
| ----------- | ---------- | ---------- | ---------- |
| Word count  | 718        | 834        | 844        |
| Sections    | 14         | 16         | 13         |
| Subsections | 0          | 1          | 14         |

| Tier                   | run1-c1000 | run2-c1000 | run3-c1000 |
| ---------------------- | ---------- | ---------- | ---------- |
| Must (out of 8)        | 6+ 1±      | 5+ 2±      | 5+ 1±      |
| Should (out of 16)     | 5+ 9±      | 6+ 8±      | 6+ 8±      |
| Could (out of 17)      | 4+         | 3+         | 3+         |
| Total points (145 max) | 102        | 94         | 91         |
| **Score**              | **70%**    | **65%**    | **63%**    |
