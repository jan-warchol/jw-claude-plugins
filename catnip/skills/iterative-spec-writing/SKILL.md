---
name: iterative-spec-writing
description: >
  Write a spec through an iterative workflow.
  Stores all intermediate files in .catnip/<timestamp>-<slug>/ in the project directory.
---

Orchestrate iterative spec writing for a user request.

## Required inputs

Collect before proceeding:

- **request**: the user's request (ask if not provided as skill argument)

## Setup

1. Choose a 3–8 word slug from the request: lowercase words joined with hyphens
   (e.g. `oauth-token-refresh`).
2. Create the working directory:
   ```
   .catnip/<YYYYMMDDTHHMMSS>-<slug>/
   ```
   where the timestamp is the current local time in `YYYYMMDDTHHMMSS` format.
3. Write `metadata.json` in that directory:
   ```json
   {
     "user_request": "<user request copied verbatim>",
   }
   ```

## Steps

Run the following subskills in order, passing the working directory path as the argument to each:

1. **`draft-spec`** — save the output as `initial.md` in the working directory
2. **`enrich-spec`** — save the output as `enriched.md` in the working directory
3. **`compress-spec`** — save the output as `compressed.md` in the working directory

## Result

After all three steps complete, save the `compressed` spec to the project root, as `<slug>.md`.
