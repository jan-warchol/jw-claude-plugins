## Creating reference plans

Use the following prompt 3 times, save as `plan-1.md`, `plan-2.md`, `plan-3.md`:

    <base-plan-prompt.txt> <task>

Let claude compare the plans:

    In this directory you can find 3 plans written for the same feature. Read them and compare. Focus more on the structure (for example, does each plan discuss what is out of scope?) rather than solution details (however, if the overall approaches are significantly different, mention that).

And create a "median" version:

    Prepare a "median plan" by averaging out these plans: use a structure that is representative to the whole group, and include only information that appears in at least 2 out of 3 plans. Save the plan as `typical-plan.md`.

Then, create a "superset" version that includes insights from all attempts:

    Now create a "superset plan" that incorporates all good elements from all plans. When plans don't agree on some detail, choose by following the majority. Keep the overall size of the resulting plan similar to the input plans. Save as `combined-plan.md`.

And finally a version condensed to desired size:

    Now condense the combined plan to be no longer than 400 words, keeping as much valuable information as possible. You can drop some of the content - in particular, omit information that you think is least important or could be most easily inferred. Note: only words with letters count towards the limit - punctuation and markdown formatting such as ### 1. 2. |----| are not counted, so you can use formatting freely. Save as condensed-plan.md.
