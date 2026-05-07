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
    "Agent(subagent_type=\"simulated-user:simulated-user\", prompt=\"<your numbered questions>\"). "
    "Do not ask the human user anything — all answers come from the simulated user."
)

ASK_USER_BLOCK_REASON = (
    "Simulation mode is active. AskUserQuestion is disabled. "
    "Ask your questions via Agent(subagent_type=\"simulated-user:simulated-user\", prompt=\"<your numbered questions>\") instead."
)


def config_exists() -> bool:
    cwd = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    return (cwd / CONFIG_FILE).exists()


def handle_user_prompt_submit(data: dict) -> None:
    if not config_exists():
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": SIMULATION_REMINDER,
        }
    }))


def handle_allow_simulated_user_read(data: dict) -> None:
    if data.get("agent_type") != "simulated-user":
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }))


def handle_validate_config(data: dict) -> None:
    content = data.get("tool_input", {}).get("content", "")
    try:
        config = json.loads(content)
    except json.JSONDecodeError:
        sys.exit(0)

    missing = [
        f for f in config.get("knowledge_files", [])
        if not Path(f).exists()
    ]
    if not missing:
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Knowledge file(s) not found: {', '.join(missing)}",
        }
    }))


def handle_block_ask_user(data: dict) -> None:
    if not config_exists():
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": ASK_USER_BLOCK_REASON,
        }
    }))


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    data = json.loads(sys.stdin.read())

    if event == "UserPromptSubmit":
        handle_user_prompt_submit(data)
    elif event == "AllowSimulatedUserRead":
        handle_allow_simulated_user_read(data)
    elif event == "ValidateConfig":
        handle_validate_config(data)
    elif event == "BlockAskUser":
        handle_block_ask_user(data)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
