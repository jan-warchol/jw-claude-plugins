#!/usr/bin/env python3
"""PreToolUse hook: block Write of .md files whose body word count violates limits.

Limits are derived from the `complexity` field in YAML frontmatter.
"""

import json
import re
import sys
from pathlib import Path

_FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)


def _parse_frontmatter(content: str) -> tuple[str | None, str]:
    """Return (frontmatter_text, body_text), or (None, content) if no valid block."""
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    return m.group(1), content[m.end() :]


def _get_complexity(frontmatter: str) -> int | None:
    """Return complexity int, None if key absent, raise ValueError if key present but invalid."""
    for line in frontmatter.splitlines():
        if re.match(r"^complexity\s*:", line):
            value = line.split(":", 1)[1].strip()
            return int(value)
    return None


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if event.get("tool_name") != "Write":
        sys.exit(0)

    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path.endswith(".md"):
        sys.exit(0)

    content = tool_input.get("content", "")
    frontmatter, body = _parse_frontmatter(content)
    if frontmatter is None:
        sys.exit(0)

    try:
        complexity = _get_complexity(frontmatter)
    except ValueError:
        print(
            f"WARNING: plan-word-count: {Path(file_path).name} has a non-integer"
            " 'complexity' field in frontmatter",
            file=sys.stderr,
        )
        sys.exit(0)

    if complexity is None:
        sys.exit(0)

    word_count = sum(1 for w in body.split() if re.search(r"[A-Za-z]", w))
    min_words = 50 * (complexity - 1)
    max_words = 100 * (complexity - 1)

    if word_count < min_words:
        reason = (
            f"Plan body is too short: {word_count} words for complexity {complexity}"
            f" (minimum {min_words}). Expand the plan before writing."
        )
    elif word_count > max_words:
        reason = (
            f"Plan body is too long: {word_count} words for complexity {complexity}"
            f" (maximum {max_words}). Condense the plan before writing."
        )
    else:
        sys.exit(0)

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
