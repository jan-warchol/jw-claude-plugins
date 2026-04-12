#!/usr/bin/env python3
"""Filter JSONL log files with Claude Code events by removing selected fields.

Writes to <input-stem>-filtered.<extension>.
"""

import json
import sys
from pathlib import Path
from utils import (
    EVENTS_FILE,
    FILTERED_EVENTS_FILE,
    get_log_dir,
    load_config,
    read_jsonl,
)


LEADING_KEYS = ["timestamp", "session_id", "hook_event_name"]

TOP_LEVEL_BLACKLIST = {
    # "timestamp",
    # "session_id",
    "cwd",
    "transcript_path",
    "agent_transcript_path",
    "permission_mode",
    "agent_id",
    "tool_use_id",
    "source",
    "permission_suggestions",
}

TOOL_INPUT_BLACKLIST = {
    "content",
    "new_string",
    "old_string",
    "offset",
    "head_limit",
    "replace_all",
    "limit",
    "output_mode",
    # "description"  # Not useful for bash commands, but useful for agents and tasks
}


def should_skip(entry):
    event = entry.get("hook_event_name")
    tool = entry.get("tool_name")
    if event == "PermissionRequest" and tool == "AskUserQuestion":
        return True
    if event == "PostToolUse" and tool != "AskUserQuestion":
        return True
    if event == "UserPromptSubmit":
        # Weird events that are not actually user prompts.
        stripped = entry.get("prompt", "").strip()
        if stripped.startswith("<task-notification>") and stripped.endswith(
            "</task-notification>"
        ):
            return True
    return False


def trim_long(text, limit=1000, head=400, tail=400):
    if len(text) > limit:
        return text[:head] + "[...................................]" + text[-tail:]
    return text


def filter_entry(entry):
    remaining = {k: v for k, v in entry.items() if k not in TOP_LEVEL_BLACKLIST}
    result = {k: remaining.pop(k) for k in LEADING_KEYS if k in remaining}
    result.update(remaining)
    if "tool_input" in result:
        result["tool_input"] = {
            k: v
            for k, v in result["tool_input"].items()
            if k not in TOOL_INPUT_BLACKLIST
        }

    # Keep just the answers in postToolUse AskUserQuestion events.
    tool = entry.get("tool_name")
    event = entry.get("hook_event_name")
    if event == "PostToolUse" and tool == "AskUserQuestion":
        del result["tool_input"]
        del result["tool_response"]["questions"]

    if event == "PermissionRequest" and tool == "ExitPlanMode":
        del result["tool_input"]
        del result["tool_response"]["questions"]

    if "last_assistant_message" in result:
        result["last_assistant_message"] = trim_long(
            result["last_assistant_message"], head=300, tail=600
        )
    return result


if __name__ == "__main__":
    if len(sys.argv) == 1:
        log_dir = get_log_dir(load_config())
        in_path = log_dir / EVENTS_FILE
        out_path = log_dir / FILTERED_EVENTS_FILE
    elif len(sys.argv) == 2:
        in_path = Path(sys.argv[1])
        out_path = in_path.with_name(in_path.stem + "-filtered" + in_path.suffix)
    else:
        print("Usage: filter_events.py [input_file]", file=sys.stderr)
        sys.exit(1)
    with open(out_path, "w") as f_out:
        for entry in read_jsonl(in_path):
            if should_skip(entry):
                continue
            filtered = filter_entry(entry)
            f_out.write(json.dumps(filtered) + "\n")
    print(f"filtered {in_path} -> {out_path}", file=sys.stderr)
