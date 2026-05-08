# CATNIP

**Complexity-Aware Task Navigation and Intelligent Planning**

A Claude Code plugin that adjusts model behavior based on the assessed complexity of each user request.

## Skills

- `catnip:complexity-aware-plan` - Create a spec/plan with depth and composition based on task complexity
  specified by the user on a 1-10 scale.

Guidelines for specifying complexity:

- **Level 1**: Simple questions, straightforward edits to a single file.
  1-10 lines of output, no reasoning required.
- **Level 3**: Changes across several files, simple self-contained script
  using one external API or a question requiring some research.
  10-100 lines of output, reasoning required.
- **Level 5**: Complete implementation of a single moderately complex feature
  in a software project, including writing tests and updating documentation.
  100-1000 lines of output.
- **Level 10**: Designing and implementing a complex software project.
  30,000+ lines of expected output, extensive reasoning and planning.
