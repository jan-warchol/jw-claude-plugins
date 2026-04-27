#!/usr/bin/env python3
"""Single entry point for complexity-assessment hooks.

Usage: hooks.py <EventName>

EventName must match one of the Claude Code hook events: PermissionRequest,
PreToolUse, PostToolUse, UserPromptSubmit. Event payload is read from stdin.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Utils (shared helpers)
# ---------------------------------------------------------------------------

ASSESSMENTS_LOG_FNAME = "complexity-logs.jsonl"
CURRENT_TASK_FNAME = ".catnip-task-complexity.json"

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
    path = get_log_dir() / ASSESSMENTS_LOG_FNAME
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# SessionStart: clear stale complexity file from previous session
# ---------------------------------------------------------------------------


def clear_task_complexity_file(_event: dict) -> None:
    Path(CURRENT_TASK_FNAME).unlink(missing_ok=True)


def on_session_start(_event: dict) -> None:
    clear_task_complexity_file(_event)
    print(
        "For each new user request, start by evaluating it with the assessing-complexity skill. Include user request verbatim as the skill args."
    )


# ---------------------------------------------------------------------------
# PermissionRequest: auto-approve Write tool calls that log task complexity
# ---------------------------------------------------------------------------


def _parse_complexity_write_tool(event: dict) -> dict | None:
    if event.get("tool_name") != "Write":
        return None
    tool_input = event.get("tool_input", {})
    if (
        Path(tool_input.get("file_path", "")).resolve()
        != Path(CURRENT_TASK_FNAME).resolve()
    ):
        return None
    try:
        payload = json.loads(tool_input.get("content", ""))
    except json.JSONDecodeError:
        return None
    if isinstance(payload.get("rating"), (int, float)) and isinstance(
        payload.get("input"), str
    ):
        return payload
    return None


def approve_complexity_write(event: dict) -> None:
    if _parse_complexity_write_tool(event) is None:
        return
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


# ---------------------------------------------------------------------------
# PostToolUse: log complexity from file content and clean up the file
# ---------------------------------------------------------------------------


def log_complexity_write(event: dict) -> None:
    payload = _parse_complexity_write_tool(event)
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


def _log_git_overview() -> None:
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return
    result = subprocess.run(
        ["git", "ls", "--no-color"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    ts = int(time.time())
    snapshots_dir = Path(".debug")
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    (snapshots_dir / f"{ts}_git_overview").write_text(output)


def log_skill_invocation(event: dict) -> None:
    if event.get("tool_name") != "Skill":
        return
    if event.get("tool_input", {}).get("skill") != "catnip:assessing-complexity":
        return
    write_log_entry({"timestamp": int(time.time()), **_filter_fields(event)})
    _log_git_overview()


# ---------------------------------------------------------------------------
# UserPromptSubmit: intercept "catnip comment:" trigger, log all prompts
# ---------------------------------------------------------------------------

CATNIP_COMMENT_PREFIX = "catnip comment:"


def _amend_last_complexity_assessment(comment: str) -> bool:
    path = get_log_dir() / ASSESSMENTS_LOG_FNAME
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError:
        return False
    for i in reversed(range(len(lines))):
        try:
            entry = json.loads(lines[i])
        except json.JSONDecodeError:
            continue
        if entry.get("hook_event_name") == "ComplexityAssessment":
            entry["user_comment"] = comment
            lines[i] = json.dumps(entry)
            path.write_text("\n".join(lines) + "\n")
            return entry
    return False


def on_user_prompt(event: dict) -> None:
    prompt: str = event.get("prompt", "")
    if prompt.lower().startswith(CATNIP_COMMENT_PREFIX):
        comment = prompt[len(CATNIP_COMMENT_PREFIX) :].strip()
        entry = _amend_last_complexity_assessment(comment)
        reason = (
            f"\nPrompt intercepted; comment recorded:\n{json.dumps(entry, indent=2)}"
        )
        print(json.dumps({"decision": "block", "reason": reason}))
        return
    clear_task_complexity_file(event)
    write_log_entry({"timestamp": int(time.time()), **_filter_fields(event)})


# ---------------------------------------------------------------------------
# Main routing
# ---------------------------------------------------------------------------

HANDLERS = {
    "SessionStart": on_session_start,
    "PermissionRequest": approve_complexity_write,
    "PreToolUse": log_skill_invocation,
    "PostToolUseWrite": log_complexity_write,
    "UserPromptSubmit": on_user_prompt,
}


def main() -> None:
    if os.environ.get("CATNIP_DISABLE"):
        sys.exit(0)

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <HandlerName>", file=sys.stderr)
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
