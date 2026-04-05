#!/usr/bin/env python3
"""Filter JSONL log files with Claude Code events by removing selected fields.

Writes to <input-stem>-filtered.<extension>.
"""

import json
import sys
from pathlib import Path
from utils import EVENTS_FILE, FILTERED_EVENTS_FILE, get_log_dir, load_config, read_jsonl

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
        stripped = entry.get("prompt", "").strip()
        if stripped.startswith("<task-notification>") and stripped.endswith("</task-notification>"):
            return True
    return False


def trim_long(text, limit=250, head=100, tail=100):
    if len(text) > limit:
        return text[:head] + "[...]" + text[-tail:]
    return text


def filter_entry(entry):
    result = {k: v for k, v in entry.items() if k not in TOP_LEVEL_BLACKLIST}
    if "tool_input" in result:
        result["tool_input"] = {
            k: v
            for k, v in result["tool_input"].items()
            if k not in TOOL_INPUT_BLACKLIST
        }
    # if "tool_input" in result and "command" in result["tool_input"]:
    #     result["tool_input"]["command"] = trim_long(result["tool_input"]["command"])
    # if "last_assistant_message" in result:
    #     result["last_assistant_message"] = trim_long(result["last_assistant_message"])
    # if "agent_type" in result:  # Just to reorder it to the end for better readability.
    #     result["agent_type"] = result.pop("agent_type")
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
