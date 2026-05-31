# Scoring-quality findings: contradictions vs. technical-evaluation reports

Analysis of whether the existing technical-evaluation reports scored the candidate specs
correctly, cross-referenced against the independently-produced `contradictions.md` files.

Reports checked:

- `cc-base/evaluation-report.md`
- `catnip-phased-manual-5d0e14e/01/evaluation-report.md`
- `catnip-phased-manual-5d0e14e/02/evaluation-report.md`
- `catnip-phased-manual-5d0e14e/03/evaluation-report.md`

Reference for "truth": `cc-base/contradictions.md` and
`catnip-phased-manual-5d0e14e/contradictions.md` (these were produced with more care than the
scoring pass and are treated as the ground truth here).

---

## Verdict

There is a **systematic** scoring failure: criteria that were present but **contradicted** by the
spec were frequently scored as positive (full credit) or as 0 (absent), instead of negative. The
evaluator scored on *topic presence*, not on *direction of meaning*.

---

## Pattern A — topic matched, spec says the opposite, scored full positive

The dominant error. Most blatant case, the NaN/missing-values criterion:

| Criterion                              | Spec's actual behavior         | contradictions.md      | Report score            |
| -------------------------------------- | ------------------------------ | ---------------------- | ----------------------- |
| "NaN/missing: skip and connect across" | breaks the line / visible gap  | cc-base D1 (all three) | **+3** (cc-base L72)    |
| same                                   | breaks the line                | manual #2 (01)         | **+3** (01 report L71)  |
| same                                   | breaks the line                | manual #2 (02)         | **+3** (02 report L72)  |
| same                                   | breaks the line                | manual #2 (03)         | **+3** (03 report L74)  |

- Correct score is **−3** (contradiction), so each affected spec is ~6 points too high on this row
  alone.
- This row was mis-scored in **every** report and **every** variant (initial / enriched / c-1500 /
  c-1000), and carries **no entry** in any report's "non-obvious scores" notes — i.e. the direction
  was never examined. The evaluator saw "NaN is discussed" and awarded the points.

## Pattern B — contradiction scored as 0 (absent) instead of negative

The evaluator treats "spec does the opposite" the same as "spec is silent":

| Criterion (tier)                       | Spec behavior                       | contradictions.md       | Report score        | Should be |
| -------------------------------------- | ----------------------------------- | ----------------------- | ------------------- | --------- |
| Tick placement matches label precision | rounds labels to `1.2M` / `3.4B`    | cc-base D6 (spec-1,2)   | **0** (cc-base L69) | −3        |
| Drawing order bands → lines → points   | paints bands *on top of* lines      | cc-base D3 (spec-1,3)   | **0** (cc-base L82) | −1        |
| Bands: edges drawn independently       | forces band edges to share X array  | manual #4 (02,03)       | **0**               | −1        |
| Programmatic multi-independent highlight| single-target highlight only       | cc-base D7 (all three)  | **0** (cc-base L91) | −1        |

## Pattern C — the only correctly-scored contradiction was an explicit rebuttal

cc-base **D4** (spec-2 builds Path2D in pixel coords and *argues against* the reference's
zoom-normalized approach in prose) is scored **−10** (cc-base L62) — correctly. This is the one
case where the spec explicitly stated its disagreement. Conclusion: the evaluator only catches a
contradiction when the spec spells out its opposition, not when it quietly does the opposite.

## Pattern D — the two analysis passes disagree on facts and were never reconciled

manual contradiction **#3** states spec-01 flushes the Path2D cache on resize. The 01 report scores
the Path2D criterion **+10** (M6, L61) with a note claiming the cache "never invalidate[s] … only
data changes." One of the two passes misread the spec. The contradiction-analysis pass was clearly
more careful; the scoring pass never cross-checked against it.

---

## Root cause

The skill **already** says to "check … whether its meaning is consistent with the expectation" and
to assign "negative full points if the spec contradicts the criterion." So the rule exists — but it
is not *salient* enough to change behavior, and nothing forces the evaluator to record the spec's
actual stance before scoring. Directional criteria don't name the common wrong alternative, so the
opposite stance is not recognized as a contradiction.

---

## Recommendations

### 1. Add contrast cues to directional criteria (criteria file)

Name the anti-pattern inline so the opposite stance is recognizable as a contradiction, e.g.:

- `NaN/missing: skip and connect across — NOT a path break/visible gap`
- `Tick placement matches label precision — rounded SI/compact labels (1.2M) contradict`
- `Hover: interpolated y at hovered x — NOT snapping to nearest defined point`
- `Highlighted series redrawn in full on overlay — NOT just a dot/marker`
- `Decimation out of scope — built-in/automatic core decimation contradicts`

### 2. Force a stance-check in the skill (technical-evaluation)

Add: *"For each positive criterion, first record the spec's actual stance in one phrase, then score.
If the stance is the opposite of the expectation, it is a contradiction (negative full points), not
an absence (0)."* Requiring the stance to be written down is what would have caught the silent
NaN +3.

### 3. Reconcile the two passes

Run contradiction-analysis first and feed its findings into technical-evaluation as scoring input,
so a documented contradiction cannot end up scored positive. The information already exists in the
`contradictions.md` files; it is simply not wired into scoring.

### On rephrasing positive → negative

Mostly **not** appropriate. For *directional* criteria (connect-across, tick precision, interpolated
hover, draw order) flipping to a negative tier would stop rewarding correct behavior and lose
information when a spec gets it right; keeping both tiers double-counts. Negative phrasing is correct
only for genuinely *invented* anti-features that aren't the negation of any positive criterion
(automatic outlier detection, bundle-size target) — those were already added to "Should Not mention."

### Net effect

Recommendations 1 + 2 fix the dominant Pattern A/B errors; recommendation 3 prevents the two passes
from silently diverging (Pattern D). The skill change alone is necessary but not sufficient — the
rule it would add already partly exists and was still not applied.
