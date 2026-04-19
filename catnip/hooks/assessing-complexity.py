#!/usr/bin/env python3
"""Single entry point for complexity-assessment hooks.

Usage: hooks.py <EventName>

EventName must match one of the Claude Code hook events: PermissionRequest,
PreToolUse, PostToolUse, UserPromptSubmit. Event payload is read from stdin.
"""

import json
import os
import shlex
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Utils (shared helpers)
# ---------------------------------------------------------------------------

COMPLEXITY_ASSESSMENTS_LOG_FILE = "complexity-logs.jsonl"
CURRENT_TASK_COMPLEXITY_FILE = Path(".cc-current-task-complexity.json")

_FIELDS_TO_DROP = {"transcript_path", "cwd", "tool_use_id", "permission_mode"}


def _filter_fields(event: dict) -> dict:
    return {k: v for k, v in event.items() if k not in _FIELDS_TO_DROP}


def _read_json(path: Path) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _base_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"])
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    else:
        return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


def _load_config() -> dict:
    base = _base_config_dir()
    config = _read_json(base / "jw-claude-plugins" / "config.json") or {}
    config.update(_read_json(base / "claude-session-reporter" / "config.json") or {})
    return config


def get_log_dir() -> Path:
    config = _load_config()
    base = config.get("logs_base_dir")
    if not base:
        log_dir = Path(".claude-history")
        log_dir.mkdir(exist_ok=True)
        return log_dir

    base_dir = Path(base).expanduser()
    if not base_dir.is_absolute():
        raise ValueError(f"logs_base_dir must be an absolute path, got: {base!r}")
    cwd = Path.cwd()
    try:
        subdir = ".".join(cwd.relative_to(Path.home()).parts)
    except ValueError:
        subdir = ".".join(cwd.parts[1:])

    log_dir = base_dir / subdir
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def write_log_entry(entry: dict) -> None:
    path = get_log_dir() / COMPLEXITY_ASSESSMENTS_LOG_FILE
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# SessionStart: clear stale complexity file from previous session
# ---------------------------------------------------------------------------


def clear_old_complexity_file(_event: dict) -> None:
    CURRENT_TASK_COMPLEXITY_FILE.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# PermissionRequest: auto-approve Bash commands logging task complexity, like:
# echo '{"rating":<number>,"input":"<string>"}' > .cc-current-task-complexity.json
# ---------------------------------------------------------------------------


def _parse_complexity_write_command(command: str) -> dict | None:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None

    if len(tokens) != 4:
        return None
    if tokens[0] != "echo":
        return None
    if tokens[2] != ">":
        return None
    if Path(tokens[3]).resolve() != CURRENT_TASK_COMPLEXITY_FILE.resolve():
        return None

    try:
        payload = json.loads(tokens[1])
    except json.JSONDecodeError:
        return None

    if isinstance(payload.get("rating"), (int, float)) and isinstance(
        payload.get("input"), str
    ):
        return payload
    return None


def _approve_permission() -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": {"behavior": "allow"},
                }
            }
        )
    )


def approve_complexity_write(event: dict) -> None:
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if _parse_complexity_write_command(command) is None:
        return
    _approve_permission()


def log_complexity_write(event: dict) -> None:
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    payload = _parse_complexity_write_command(command)
    if payload is None:
        return
    write_log_entry(
        {
            "timestamp": int(time.time()),
            "session_id": event.get("session_id"),
            "hook_event_name": "ComplexityAssessment",
            **payload,
        }
    )


# ---------------------------------------------------------------------------
# PreToolUse: log invocations of the assessing-complexity skill
# ---------------------------------------------------------------------------


def log_skill_invocation(event: dict) -> None:
    if event.get("tool_name") != "Skill":
        return
    if event.get("tool_input", {}).get("skill") != "catnip:assessing-complexity":
        return
    write_log_entry({"timestamp": int(time.time()), **_filter_fields(event)})


# ---------------------------------------------------------------------------
# UserPromptSubmit: log all prompts
# ---------------------------------------------------------------------------


def log_user_prompt(event: dict) -> None:
    write_log_entry({"timestamp": int(time.time()), **_filter_fields(event)})


# ---------------------------------------------------------------------------
# Main routing
# ---------------------------------------------------------------------------

HANDLERS = {
    "SessionStart": clear_old_complexity_file,
    "PermissionRequest": approve_complexity_write,
    "PreToolUse": log_skill_invocation,
    "PreToolUseBash": log_complexity_write,
    "UserPromptSubmit": log_user_prompt,
}


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <EventName>", file=sys.stderr)
        sys.exit(1)

    event_name = sys.argv[1]
    handler = HANDLERS.get(event_name)
    if handler is None:
        print(f"Unknown event: {event_name}", file=sys.stderr)
        sys.exit(1)

    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    handler(event)


if __name__ == "__main__":
    main()
