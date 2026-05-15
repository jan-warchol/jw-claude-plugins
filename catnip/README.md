# CATNIP

**Complexity-Aware Task Navigation and Intelligent Planning**

A Claude Code plugin that adjusts model behavior based on the assessed complexity of each user request.


## Installation


First, register the marketplace. Assuming you have SSH authentication configured:

```
/plugin marketplace add git@github.com:jan-warchol/jw-claude-plugins.git
```

Then install the plugin itself:

```
/plugin install catnip@jan-warchol-plugins
```


## Skills

- `catnip:complexity-aware-spec` - Create a spec with depth and composition based on task complexity
  specified by the user on a 1-10 scale. Note that the skill can only be invoked directly by the user
  (not by the model), so you must use full skill name to trigger it.

Example usage:

```
/catnip:complexity-aware-spec Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments. complexity: 3
```

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
