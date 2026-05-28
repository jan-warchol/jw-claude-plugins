## By Eval Type

| Directory | Struct avg | Struct min | Struct max | Tech avg | Tech min | Tech max | WC avg | WC min | WC max |
|---|---|---|---|---|---|---|---|---|---|
| with-assumptions-no-reorganize | 16.2 | 15 | 17 | 90.7% | 85% | 98% | 368 | 353 | 377 |
| with-assumptions | 15.9 | 15 | 17 | 91.3% | 88% | 97% | 387 | 330 | 417 |
| with-outline-structure | 14.9 | 13 | 17 | 89.7% | 82% | 96% | 358 | 299 | 414 |
| auto-evals | 12.3 | 10 | 14 | 88.0% | 78% | 99% | 365 | 335 | 396 |
| auto-with-adjusted-inputs | 13.9 | 12 | 16 | 85.0% | 85% | 85% | 353 | 271 | 415 |
| manual-prompt | 12.2 | 8 | 15 | 88.3% | 84% | 91% | 300 | 285 | 316 |

## By Aggregation Type

| Directory | Struct avg | Tech avg | WC avg | Struct min | Tech min | WC min | Struct max | Tech max | WC max |
|---|---|---|---|---|---|---|---|---|---|
| with-assumptions-no-reorganize | 16.2 | 90.7% | 368 | 15 | 85% | 353 | 17 | 98% | 377 |
| with-assumptions | 15.9 | 91.3% | 387 | 15 | 88% | 330 | 17 | 97% | 417 |
| with-outline-structure | 14.9 | 89.7% | 358 | 13 | 82% | 299 | 17 | 96% | 414 |
| auto-evals | 12.3 | 88.0% | 365 | 10 | 78% | 335 | 14 | 99% | 396 |
| auto-with-adjusted-inputs | 13.9 | 85.0% | 353 | 12 | 85% | 271 | 16 | 85% | 415 |
| manual-prompt | 12.2 | 88.3% | 300 | 8 | 84% | 285 | 15 | 91% | 316 |

## Detailed Breakdown

| Directory | Sample | Word Count | Struct (runs) | Tech |
|---|---|---|---|---|
| with-assumptions-no-reorganize | 01 | 377 | 15, 17, 16 | 98% |
| with-assumptions-no-reorganize | 02 | 353 | 16, 16, 16 | 89% |
| with-assumptions-no-reorganize | 03 | 375 | 17, 16, 17 | 85% |
| with-assumptions | 01 | 330 | 15, 15, 15 | 88% |
| with-assumptions | 02 | 417 | 17, 17, 17 | 89% |
| with-assumptions | 03 | 413 | 15, 16, 16 | 97% |
| with-outline-structure | 01 | 346 | 16, 15, 16 | 91% |
| with-outline-structure | 02 | 371 | 14, 15, 15 | 82% |
| with-outline-structure | 03 | 310 | 13, 13, 13 | 91% |
| with-outline-structure | 04 | 414 | 16, 15, 15 | 93% |
| with-outline-structure | 05 | 299 | 15, 15, 15 | 85% |
| with-outline-structure | 06 | 408 | 17, 16, 15 | 96% |
| auto-evals | 01 | 342 | 14 | 99% |
| auto-evals | 02 | 335 | 10 | 98% |
| auto-evals | 03 | 396 | 12 | 78% |
| auto-evals | 04 | 392 | 12, 11, 14 | 80% |
| auto-evals | 05 | 355 | 13, 13, 12 | 86% |
| auto-evals | 06 | 371 | 13, 12, 12 | 87% |
| auto-with-adjusted-inputs | 01 | 415 | 16, 14, 16 | 85% |
| auto-with-adjusted-inputs | 02 | 271 | 13, 13, 13 | 85% |
| auto-with-adjusted-inputs | 03 | 372 | 14, 14, 12 | 85% |
| manual-prompt | 01 | 285 | 13 | 84% |
| manual-prompt | 02 | 316 | 15 | 90% |
| manual-prompt | 03 | 299 | 8, 12, 13 | 91% |
