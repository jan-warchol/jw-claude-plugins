#!/usr/bin/env python3
"""Summarize Claude history JSONL into a per-session JSON file.

Output structure:
[
  {
    "session_id": "<session_id>",
    "model": "<model>",
    "first_event": "<ISO 8601 datetime>",
    "last_event": "<ISO 8601 datetime>",
    "important_events": [
      {"prompt": "..."},   // UserPromptSubmit
      {"agent_reply": "..."},    // Stop
      {"skill": "..."},    // PreToolUse Skill
      ...
    ]
  },
  ...
]

Sessions with no important events are omitted. The list is sorted by first_event.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils import (
    FILTERED_EVENTS_FILE,
    SESSION_SUMMARIES_FILE,
    get_log_dir,
    load_config,
    read_jsonl,
)


def process(in_path: Path) -> dict:
    sessions = {}

    for entry in read_jsonl(in_path):
        event = entry.get("hook_event_name")
        sid = entry.get("session_id")
        if not sid:
            continue

        if sid not in sessions:
            sessions[sid] = {
                "model": None,
                "first_event": None,
                "last_event": None,
                "important_events": [],
            }

        s = sessions[sid]
        ts = entry.get("timestamp")
        if ts is not None:
            if s["first_event"] is None or ts < s["first_event"]:
                s["first_event"] = ts
            if s["last_event"] is None or ts > s["last_event"]:
                s["last_event"] = ts

        if event == "SessionStart":
            model = entry.get("model")
            if model:
                s["model"] = model

        elif event == "UserPromptSubmit":
            prompt = entry.get("prompt")
            if prompt:
                s["important_events"].append({"prompt": prompt})

        elif event == "PreToolUse" and entry.get("tool_name") == "Skill":
            skill = (entry.get("tool_input") or {}).get("skill")
            if skill:
                s["important_events"].append({"skill": skill})

        elif event == "PreToolUse" and entry.get("tool_name") == "Agent":
            subagent_type = (entry.get("tool_input") or {}).get(
                "subagent_type"
            ) or "<unknown type>"
            description = (entry.get("tool_input") or {}).get(
                "description"
            ) or "<no description>"
            if subagent_type or description:
                s["important_events"].append(
                    {"subagent": f"{subagent_type}: {description}"}
                )

        elif event == "PostToolUse" and entry.get("tool_name") == "AskUserQuestion":
            answers = (entry.get("tool_response") or {}).get("answers")
            if answers:
                s["important_events"].append(answers)

        elif event == "Stop":
            msg = entry.get("last_assistant_message")
            if msg:
                s["important_events"].append({"agent_reply": msg})

    return sessions


def to_iso(ts):
    return (
        datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        if ts is not None
        else None
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        log_dir = get_log_dir(load_config())
        in_path = log_dir / FILTERED_EVENTS_FILE
        out_path = log_dir / SESSION_SUMMARIES_FILE
    elif len(sys.argv) == 2:
        in_path = Path(sys.argv[1])
        out_path = in_path.with_name(in_path.stem + "-summary.json")
    else:
        print("Usage: summarize_history.py <input.jsonl>", file=sys.stderr)
        sys.exit(1)

    sessions_by_id = process(in_path)

    result = []
    for sid, session in sessions_by_id.items():
        if not session["important_events"]:
            continue
        session["session_id"] = sid
        session["first_event"] = to_iso(session["first_event"])
        session["last_event"] = to_iso(session["last_event"])
        result.append(session)

    result.sort(key=lambda s: s["first_event"] or "")

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    print(f"wrote {len(result)} sessions to {out_path}", file=sys.stderr)
