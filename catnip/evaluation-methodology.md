# Evaluating CATNIP — methodology takeaways

**Purpose.** Captures the conceptual decisions from a design discussion about how to evaluate
CATNIP-generated specs. Two audiences: (1) the domain expert who originated most of these
concerns, for review; (2) future agents working on this project, as standing context.

**Provenance.** Many of the sharpest points below were first raised by the domain expert (author
of the massive-plot-lib reference spec). His ruling is still pending on the bucket partition
(`massive-plot-lib/bucketing-draft.md`) and on the open questions at the end.

---

## What CATNIP is, and what we're measuring

CATNIP is a plugin meant to produce **better specs/plans than base Claude Code**. Per the README
it fights two failure modes: (a) plans that are **too verbose**, and (b) plans that **miss
important sections** (assumptions, risks, verifiable criteria) or **fail to clarify crucial
decisions with the user**. A second motivating data point: the `grill-me` skill asks ~20 questions
where only ~3 are crucial — pushing design onto the user. CATNIP should do the opposite: do the
work, involve the user only where it must.

The benchmark generates specs by different methods (base CC, CATNIP, …) **on the same model**,
from a prompt, and scores them. `massive-plot-lib` is the first case.

---

## The two problems that started this

1. **The prompt leaks the answers.** The reverse-engineered prompt was _compressed from the spec_,
   so it already contains design decisions a real user would not have pre-made. Feeding it to
   CATNIP tests copying, not the work CATNIP exists to do.
2. **Reference-matching measures mimicry, not quality.** The reference spec is _one opinionated
   valid design among many_. Scoring "did the generated spec reach the same architecture"
   penalizes good divergent specs. (Also: the human reviewer is not a domain expert and can't
   referee architecture on the merits — so coverage-of-concerns is judgeable,
   correctness-of-architecture is not.)

The expert added a third, deeper one: the whole case is **laboratory-artificial** (the prompt came
from days of his own iteration — the very work CATNIP automates), so even a perfect evaluation
here **may not generalize** to normal examples.

---

## Core principles reached

### 1. Separate _stability_ from _validity_

- **Stability** = does the evaluator give the same score for the same spec across runs? (evaluator
  variance)
- **Validity** = do the criteria measure the thing CATNIP is actually for?

The two problems above are **validity** problems. The current case is **fine for stability, broken
for validity**. Decision: focus on validity now; salvage examples for stability testing later.
They don't compete for the same example.

### 2. Score the _gap_, never the absolute

Because both arms run on the same model, the shared model knowledge cancels in the
**base-vs-CATNIP difference**. The benchmark's claim must always be **"CATNIP beats base by X,"
never "CATNIP scored 84%."** Absolute scores drift upward as models improve; the gap is the
durable signal. This is the backbone that keeps the benchmark **model-invariant**.

### 3. Assistant, not author — but lean on model knowledge _maximally_

CATNIP should use the model's domain knowledge as hard as possible (that's its value for
non-expert users), **and** surface the few decisions the user must own — with a **recommendation**
in every case, so the user is never left alone with the design. These don't conflict; see #5.

### 4. The `must-ask` definition

> **must-ask ⟺ the answer lives in the user's head — no domain knowledge can derive it.**

This is sharper than "important AND not in the prompt." A key decision with one clearly-best
answer (the expert's gmail-API example) is **deducible**, not must-ask, even though it's
important.

Two flavors of must-ask:

- **`[stated]`** — the user knows the question exists, just hasn't answered it.
- **`[blind-spot]`** — the user _doesn't know the question exists_. A requirement has an obviously
  best implementation that carries a large hidden trade-off elsewhere. Knowledge's job is to _find
  and frame_ it; the user still owns the choice.

### 5. Knowledge frames decisions; it never silently makes one that's the user's

This is the reconciliation of #3 and #4, and the principle to carve in stone. The `[blind-spot]`
case is the purest form: **maximal** knowledge use (to discover the hidden trade-off) in service
of a **must-ask** (only the user can weigh the trade-off). "Lean on knowledge" and "don't decide
must-asks" stop being opposites once you see knowledge operates at the _framing_ layer, not the
_deciding_ layer.

Corollary on scoring: a correct **silent guess** on a must-ask earns **no credit** (boundary
cases: penalty), because rewarding it would reward model knowledge — the one term we can't control
and that drifts with model version.

### 6. You cannot measure question quality from the artifact alone

A finished spec doesn't show what was asked. Artifact-only scoring **rewards over-asking** (ask
everything → maximally complete spec), which is anti-correlated with CATNIP's core requirement.
Question quality has three signals, and volume only covers one:

- **Restraint** — how many were asked (trivial to eyeball; catches the loud "asks everything").
- **Recall** — of what _should_ have been asked, how much was (catches silent guessing of
  must-asks).
- **Precision** — of what was asked, how much was actually warranted (catches mis-targeting).

Volume is blind to recall and precision. Both require a list of _which_ questions were warranted —
i.e. the must-ask bucket. **Note:** good recommendations _mask_ redundant questions (a smooth "I
recommend X, ok?" is easy to nod through), so intuition alone under-detects over-asking.

### 7. One partition, three instruments

The bucket partition (below) is not just scoring criteria. The same artifact serves as:

1. the **scoring criteria**, 2. the **answer-key** for manual question review, 3. the **persona
   for a user-proxy** (which must answer must-asks from a fixed key and _deflect_ deducible ones,
   or it can't expose over-asking). Getting the partition right unblocks every measurement path at
   once.

---

## The bucket partition (construction)

Rewriting the prompt and building the criteria are **the same act**: partition the reference
spec's content into five buckets. See `massive-plot-lib/bucketing-draft.md` for the worked
example.

| Bucket         | Definition                                                               | Scoring rule                                                            |
| -------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| **Prompt**     | Genuine user-side knowledge — the _problem_. Becomes the thinned prompt. | Not scored (it's the input).                                            |
| **Must-ask**   | Resolution needs something only the user can supply.                     | Scored on **whether asked/surfaced**; correct silent guess = no credit. |
| **Deducible**  | One clear best answer derivable from knowledge.                          | Scored on **decision present & sound**; asking = mild waste.            |
| **Raise-only** | Must appear; any reasonable resolution or explicit alternative counts.   | Scored on **topic surfaced**, not which answer.                         |
| **Drop**       | Pure opinion or low-level technique.                                     | Not a criterion.                                                        |

**Who draws the line.** The `must-ask ↔ deducible` boundary is a domain judgment and must be set
by the expert, **not** by the model — a model classifies as "deducible" exactly what models like
it are confident about, which shrinks must-ask and flatters CATNIP. The current draft flags every
such call for expert ruling.

---

## Operational constraint: subagents can't ask the user

`AskUserQuestion` is not usable inside a spawned subagent (subagents run to completion without
interactive turns; ~90% confident — verify before building on it). Consequence: **running CATNIP
in a subagent silently amputates its questioning**, turning it into author-mode — the exact
dimension under test. So the pipeline splits:

- **Automatable (subagent-safe):** generating non-interactive specs; scoring finished artifacts.
- **Not automatable as-is:** the question-asking behavior — needs a real main-agent turn (a human,
  or a user-proxy conversing in plain text, or the user's planned hook-driven non-interactive
  setup).

For now the interactive runs stay **hand-driven** (low N, human answers and inspects the
transcript). Artifact-scoring can be fanned out.

---

## Decided vs. open

**Decided (conceptual spine, internally consistent):**

- Validity now / stability later, on separate examples.
- Comparative scoring (the gap, never the absolute).
- Assistant-not-author; knowledge frames, user owns must-asks (both flavors).
- Artifact-scoring automatable; question-eval interactive.
- One partition → criteria + answer-key + proxy; expert sets the deducible line.

**Open / needs expert or future work:**

- **Bucket rulings** on `bucketing-draft.md` — especially all `deducible` calls, the
  `[blind-spot]` must-asks (M4–M8), and the WebGL demotion (was a rewarded `SHOULD`, now dropped).
- **N=1 generalization (the one thing bucketing can't fix).** A perfect partition still measures
  one laboratory case. **Do not trust the CATNIP-beats-base number until a second, genuinely-naive
  example** — a real, under-iterated request — reproduces the direction. Treat massive-plot-lib as
  the case for getting the _machinery_ right, not for trusting the _conclusion_. Actively looking
  for such an example.
- **The scoring skill must grow.** `technical-evaluation` currently scores presence only
  (`mentioned & consistent`). It cannot distinguish **asked** vs **decided** vs **surfaced-as-
  alternative**, and the must-ask check must read the **question transcript**, not the spec.
- **Process-first option** (expert's suggestion): build/iterate just the question-asking stage of
  CATNIP and evaluate _that_ before wiring the full pipeline — possibly using session forking to
  fix a clean starting point for later stages.
- **Scope reduction** of the example library: optional, helps bucketing, but must not strip the
  decision-density that makes this a hard test of _prioritizing_ questions.

---

## Artifacts

| Path                                                                | Role                                                                                                            |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `massive-plot-lib/reference-spec/original-spec.md`                  | Detailed human-written source spec.                                                                             |
| `massive-plot-lib/reference-spec/condensed-1400-words.md`           | Tightened restructuring of the same.                                                                            |
| `massive-plot-lib/reference-spec/reverse-engineered-fake-prompt.md` | Compressed prompt — known-deficient (leaks answers).                                                            |
| `massive-plot-lib/tech-criteria-obsolete.md`                        | Old presence-based criteria — **deprecated** (opinionated MUSTs).                                               |
| `massive-plot-lib/bucketing-draft.md`                               | The re-partition + draft thinned prompt; **pending expert review**.                                             |
| `../../spec-evaluation/skills/technical-evaluation/`                | Presence-based scorer (must grow; see open items).                                                              |
| `../../spec-evaluation/skills/structural-evaluation/`               | Generic structure scorer (goal/requirements/scope/uncertainty) — the most CATNIP-aligned of the existing tools. |
