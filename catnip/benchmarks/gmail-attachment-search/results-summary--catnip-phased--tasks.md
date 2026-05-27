## Top-Level Comparison — Grouped by Eval Type

| Directory | Tech avg | Tech min | Tech max | Struct avg (/17) | Struct min | Struct max | WC avg | WC min | WC max |
|---|---|---|---|---|---|---|---|---|---|
| with-outline-structure | 89.7% | 82% | 96% | 14.9 | 13 | 17 | 358 | 299 | 414 |
| auto-evals             | 88.0% | 78% | 99% | 12.3 | 10 | 14 | 365 | 335 | 396 |
| adjusted-inputs        | 85.0% | 85% | 85% | 13.9 | 12 | 16 | 353 | 271 | 415 |
| manual-prompt          | 88.3% | 84% | 91% | 12.2 | 8  | 15 | 300 | 285 | 316 |

## Top-Level Comparison — Grouped by avg / min / max

| Directory | Tech avg | Struct avg | WC avg | Tech min | Struct min | WC min | Tech max | Struct max | WC max |
|---|---|---|---|---|---|---|---|---|---|
| with-outline-structure | 89.7% | 14.9 | 358 | 82% | 13 | 299 | 96% | 17 | 414 |
| auto-evals             | 88.0% | 12.3 | 365 | 78% | 10 | 335 | 99% | 14 | 396 |
| adjusted-inputs        | 85.0% | 13.9 | 353 | 85% | 12 | 271 | 85% | 16 | 415 |
| manual-prompt          | 88.3% | 12.2 | 300 | 84% | 8  | 285 | 91% | 15 | 316 |

## Detailed per-Sample Breakdown

| Directory | Sample | Word count | Structural runs (/17) | Tech score |
|---|---|---|---|---|
| with-outline-structure | 01 | 346 | 15, 16, 16 | 91% |
| with-outline-structure | 02 | 371 | 15, 15, 14 | 82% |
| with-outline-structure | 03 | 310 | 13, 13, 13 | 91% |
| with-outline-structure | 04 | 414 | 15, 15, 16 | 93% |
| with-outline-structure | 05 | 299 | 15, 15, 15 | 85% |
| with-outline-structure | 06 | 408 | 16, 15, 17 | 96% |
| auto-evals             | 01 | 342 | 14         | 99% |
| auto-evals             | 02 | 335 | 10         | 98% |
| auto-evals             | 03 | 396 | 12         | 78% |
| auto-evals             | 04 | 392 | 11, 14, 12 | 80% |
| auto-evals             | 05 | 355 | 13, 12, 13 | 86% |
| auto-evals             | 06 | 371 | 12, 12, 13 | 87% |
| adjusted-inputs        | 01 | 415 | 14, 16, 16 | 85% |
| adjusted-inputs        | 02 | 271 | 13, 13, 13 | 85% |
| adjusted-inputs        | 03 | 372 | 14, 12, 14 | 85% |
| manual-prompt          | 01 | 285 | 13         | 84% |
| manual-prompt          | 02 | 316 | 15         | 90% |
| manual-prompt          | 03 | 299 | 12, 13, 8  | 91% |
