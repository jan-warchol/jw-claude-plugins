#!/usr/bin/env python3
"""Hooks for the simulated-user plugin."""

import json
import os
import sys
from pathlib import Path

CONFIG_FILE = ".simulate-user-config.json"

SIMULATION_REMINDER = (
    "SIMULATION MODE ACTIVE: Do not use AskUserQuestion. "
    "When you need clarifying information, compile all your questions and send them "
    "to the simulated-user subagent in a single call: "
    "Agent(subagent_type=\"simulated-user\", prompt=\"<your numbered questions>\"). "
    "Do not ask the human user anything — all answers come from the simulated user."
)

ASK_USER_BLOCK_REASON = (
    "Simulation mode is active. AskUserQuestion is disabled. "
    "Ask your questions via Agent(subagent_type=\"simulated-user\", prompt=\"<your numbered questions>\") instead."
)


def config_exists() -> bool:
    cwd = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    return (cwd / CONFIG_FILE).exists()


def handle_user_prompt_submit() -> None:
    if not config_exists():
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": SIMULATION_REMINDER,
        }
    }
    print(json.dumps(output))


def handle_pre_tool_use() -> None:
    if not config_exists():
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": ASK_USER_BLOCK_REASON,
        }
    }
    print(json.dumps(output))


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    # consume stdin to avoid broken pipe
    sys.stdin.read()

    if event == "UserPromptSubmit":
        handle_user_prompt_submit()
    elif event == "PreToolUse":
        handle_pre_tool_use()
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
