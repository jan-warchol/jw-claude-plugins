## Overview

Logs all Claude Code hook events (session start/end, tool use, prompts, etc.) to a
JSONL file for later analysis. By default, logs go to `.claude-sessions/all-events.jsonl`
in the current working directory.

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
