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

_FIELDS_TO_DROP = {"transcript_path", "cwd", "tool_use_id", "permission_mode"}


def _filter_fields(event: dict) -> dict:
    return {k: v for k, v in event.items() if k not in _FIELDS_TO_DROP}


def _read_json(path: Path) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"])
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "claude-session-reporter"


def load_config() -> dict:
    return _read_json(_config_dir() / "config.json") or {}


def get_log_dir(config: dict) -> Path:
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
    path = get_log_dir(load_config()) / COMPLEXITY_ASSESSMENTS_LOG_FILE
    with open(path, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------
# SessionStart: export COMPLEXITY_LOG_FILE into the session environment
# ---------------------------------------------------------------------------


def handle_session_start() -> None:
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if env_file:
        log_path = get_log_dir(load_config()) / COMPLEXITY_ASSESSMENTS_LOG_FILE
        with open(env_file, "a") as f:
            f.write(f"export COMPLEXITY_LOG_FILE={log_path}\n")


# ---------------------------------------------------------------------------
# PermissionRequest: auto-approve the complexity assessment log-write command
# ---------------------------------------------------------------------------


def _is_complexity_log_write_command(command: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False

    if len(tokens) != 4:
        return False
    if tokens[0] != "echo":
        return False
    if tokens[2] != ">>":
        return False
    if not (
        tokens[3].endswith("complexity-logs.jsonl")
        or tokens[3] == "$COMPLEXITY_LOG_FILE"
    ):
        return False

    try:
        payload = json.loads(tokens[1])
    except json.JSONDecodeError:
        return False

    return (
        payload.get("event") == "complexity_assessment"
        and isinstance(payload.get("rating"), (int, float))
        and isinstance(payload.get("prompt"), str)
        and "timestamp" in payload
    )


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


def handle_permission_request(event: dict) -> None:
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if _is_complexity_log_write_command(command):
        _approve_permission()


# ---------------------------------------------------------------------------
# PreToolUse: log invocations of the assessing-complexity skill
# ---------------------------------------------------------------------------


def handle_pre_tool_use(event: dict) -> None:
    if event.get("tool_name") != "Skill":
        return
    if event.get("tool_input", {}).get("skill") != "catnip:assessing-complexity":
        return
    write_log_entry({"timestamp": int(time.time()), **_filter_fields(event)})


# ---------------------------------------------------------------------------
# UserPromptSubmit: log all prompts
# ---------------------------------------------------------------------------


def handle_user_prompt_submit(event: dict) -> None:
    write_log_entry({"timestamp": int(time.time()), **_filter_fields(event)})


# ---------------------------------------------------------------------------
# Main routing
# ---------------------------------------------------------------------------

HANDLERS = {
    "SessionStart": handle_session_start,
    "PermissionRequest": handle_permission_request,
    "PreToolUse": handle_pre_tool_use,
    "UserPromptSubmit": handle_user_prompt_submit,
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

    if event_name == "SessionStart":
        handle_session_start()
        return

    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    handler(event)


if __name__ == "__main__":
    main()
