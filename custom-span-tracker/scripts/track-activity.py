#!/usr/bin/env python3
"""
Track activity to .debug/current/span-info.json.

Records at span level:
  - sessions       list of session IDs that contributed events to this span
  - conversation   list of {"user": ...} and {"agent": ...} entries
  - skills_used    list of Skill tool invocations
  - subagents_used list of "{type}: {description}" strings from Agent tool calls
  - user_answers   list of answer dicts from PostToolUse[AskUserQuestion]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import utils

event = utils.load_event()
hook_event_name = event.get("hook_event_name", "")
tool_name = event.get("tool_name", "")
session_id = event.get("session_id")

span = utils.load_active_span()
if not span:
    sys.exit(0)


def record(update_fn):
    import json
    run_info = utils.read_json(utils.SPAN_INFO_FILE)
    if session_id and session_id not in run_info.setdefault("sessions", []):
        run_info["sessions"].append(session_id)
    update_fn(run_info)
    utils.SPAN_INFO_FILE.write_text(json.dumps(run_info, indent=2))


if hook_event_name == "UserPromptSubmit":
    prompt = event.get("prompt")
    if prompt:
        record(lambda d: d.setdefault("conversation", []).append({"user": prompt}))

elif hook_event_name == "Stop":
    msg = event.get("last_assistant_message")
    if msg:
        record(lambda d: d.setdefault("conversation", []).append({"agent": msg}))

elif tool_name == "Skill":
    skill_name = event.get("tool_input", {}).get("skill", "")
    if skill_name:
        record(lambda d: d.setdefault("skills_used", []).append(skill_name))

elif tool_name == "Agent":
    subagent_type = (event.get("tool_input") or {}).get("subagent_type") or "<unknown type>"
    description = (event.get("tool_input") or {}).get("description") or "<no description>"
    record(lambda d: d.setdefault("subagents_used", []).append(f"{subagent_type}: {description}"))

elif tool_name == "AskUserQuestion":
    answers = event.get("tool_input", {}).get("answers")
    if answers:
        record(lambda d: d.setdefault("user_answers", []).append(answers))

sys.exit(0)
