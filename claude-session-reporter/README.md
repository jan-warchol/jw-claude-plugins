## Overview

Logs all Claude Code hook events (tool use, prompts, etc.) to a JSONL file for later
analysis. By default, logs go to `.claude-history/` in the current working directory.

At the end of each session, the raw log is also filtered into a more readable version
with noisy fields (large tool inputs etc.) stripped out, and an event more condensed
session summary is also produced.

## Installation

```
/plugin install claude-session-reporter@jan-warchol-plugins
```

## Configuration

Logging location can be configured:

```json
{ "logs_base_dir": "~/my-logs" }
```

This would make the logs to be saved in `~/my-logs/<project-subdir>/all-events.jsonl` instead of the local directory.

The project subdirectory is derived from the working path:
- `~/src/foo/myproject` → `src.foo.myproject`
- `/opt/work/project` → `opt.work.project`

| Platform | Config file location |
|----------|----------------------|
| Linux / WSL | `$XDG_CONFIG_HOME/claude-session-reporter/config.json` (default: `~/.config/...`) |
| macOS | `~/Library/Application Support/claude-session-reporter/config.json` |
| Windows | `%APPDATA%\claude-session-reporter\config.json` |
