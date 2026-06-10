# My dev plugins for Claude Code

- `trivial-logger`: a trivial logger for collecting prompt, tool use and permission request events
  to a local file for later analysis,
- `claude-session-reporter`: Log events from Claude sessions, filter them and produce summaries for
  later analysis. All data is saved locally,
- `catnip`: Complexity-Aware Task Navigation and Intelligent Planning,
- ...more to come.

## Installation

First, register the marketplace:

```
/plugin marketplace add jan-warchol/jw-claude-plugins
```

Then install the plugins themselves:

```
/plugin install trivial-logger@jw-claude-plugins
/plugin install claude-session-reporter@jw-claude-plugins
/plugin install catnip@jan-warchol-plugins
```
