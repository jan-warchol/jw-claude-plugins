# CATNIP

**Complexity-Aware Task Navigation and Intelligent Planning**

A Claude Code plugin that adjusts model behavior based on the assessed complexity of each user request.

## Skills

- `catnip:assessing-complexity` — Rates each new request on a 1–10 scale and logs the assessment. Invoked automatically.
- **`catnip: complexity-aware-plan`** - Create a spec/plan with depth and composition based on task complexity (assessed by the skill above)
