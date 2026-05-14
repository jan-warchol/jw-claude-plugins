#!/usr/bin/env python3
"""PreToolUse hook: auto-allow operations on `.catnip/clarification-notes/`.

Auto-allows (relative to cwd):
  - Write/Read on any file under `.catnip/clarification-notes/`
  - Bash `mkdir [-p] .catnip` and `mkdir [-p] .catnip/clarification-notes`
  - Bash `ls [flags] .catnip/clarification-notes[/]`

For any other input, exits without emitting a decision (defers to other hooks
and the user's normal permission flow).
"""

import json
import re
import sys
from pathlib import Path

CATNIP_DIR = Path(".catnip")
NOTES_DIR = CATNIP_DIR / "clarification-notes"

_MKDIR_PATTERNS = [
    re.compile(r"^mkdir(?:\s+-p)?\s+\.catnip/?$"),
    re.compile(r"^mkdir(?:\s+-p)?\s+\.catnip/clarification-notes/?$"),
    re.compile(r"^mkdir\s+-p\s+\.catnip/?\s+\.catnip/clarification-notes/?$"),
]
_LS_PATTERN = re.compile(
    r"^ls(?:\s+-[A-Za-z]+)*\s+\.catnip/clarification-notes/?$"
)


def _allow(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def _is_under_notes_dir(file_path_str: str) -> bool:
    if not file_path_str:
        return False
    file_path = Path(file_path_str)
    allowed = (Path.cwd() / NOTES_DIR).resolve()
    try:
        file_path.resolve().relative_to(allowed)
    except ValueError:
        return False
    return True


def _bash_is_allowed(command: str) -> bool:
    cmd = command.strip()
    if any(p.match(cmd) for p in _MKDIR_PATTERNS):
        return True
    if _LS_PATTERN.match(cmd):
        return True
    return False


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = event.get("tool_name")
    tool_input = event.get("tool_input", {}) or {}

    if tool_name in ("Write", "Read"):
        if _is_under_notes_dir(tool_input.get("file_path", "")):
            _allow(f"{tool_name} under .catnip/clarification-notes is auto-allowed")
        sys.exit(0)

    if tool_name == "Bash":
        if _bash_is_allowed(tool_input.get("command", "")):
            _allow("mkdir/ls for .catnip/clarification-notes is auto-allowed")
        sys.exit(0)


if __name__ == "__main__":
    main()
