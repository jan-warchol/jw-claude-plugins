#!/usr/bin/env python3
"""
Handle start/stop of tracking spans.

Triggered by UserPromptSubmit (skill invoked via /custom-span-tracker:start|stop)
and PostToolUse[Skill] (skill invoked programmatically).

start: creates .debug/current/ and span-info.json
stop:  renames .debug/current/ to <span-id>[-<name>]/
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import utils

event = utils.load_event()
hook_event_name = event.get("hook_event_name", "")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def inject_context(message: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": hook_event_name,
                    "additionalContext": message,
                }
            }
        )
    )


def message_to_user(message: str) -> None:
    print(json.dumps({"systemMessage": f"\n{message}"}))


def handle_start(args: str) -> None:
    if utils.CURRENT_DIR.exists():
        inject_context("A span is already active. Run /custom-span-tracker:stop first.")
        return

    span_id = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    name = args.strip() if args else ""

    utils.CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    span_info = {
        "span_id": span_id,
        "name": name,
        "start_time": int(time.time()),
    }
    utils.SPAN_INFO_FILE.write_text(json.dumps(span_info, indent=2))

    label = f" '{name}'" if name else ""
    inject_context(f"Span{label} started (id: {span_id}).")


def handle_session_start() -> None:
    span = utils.load_active_span()
    if not span:
        return
    name = span.get("name", "").strip()
    label = f" '{name}'" if name else ""
    message_to_user(
        f"There is an active tracking span{label} (id: {span['span_id']}). "
    )


def handle_stop() -> None:
    span = utils.load_active_span()
    if not span:
        message_to_user(
            "No active span found. Run /custom-span-tracker:start to begin one."
        )
        return

    span_info = utils.read_json(utils.SPAN_INFO_FILE)
    span_info["end_time"] = int(time.time())
    utils.SPAN_INFO_FILE.write_text(json.dumps(span_info, indent=2))

    span_id = span["span_id"]
    name = span.get("name", "").strip()
    final_name = f"{span_id}-{slugify(name)}" if name else span_id
    final_dir = utils.SPANS_DIR / final_name
    utils.CURRENT_DIR.rename(final_dir)

    duration_s = span_info["end_time"] - span["start_time"]
    duration_m = duration_s // 60
    inject_context(
        f"Span stopped. Duration: {duration_m}m {duration_s % 60}s. "
        f"Data saved to .debug/{final_name}/span-info.json"
    )


if hook_event_name == "SessionStart":
    handle_session_start()

elif hook_event_name == "UserPromptSubmit":
    prompt = event.get("prompt", "") or ""

    if re.search(r"/custom-span-tracker:start\b", prompt):
        args_match = re.search(r"/custom-span-tracker:start\s+(.*)", prompt)
        args = args_match.group(1).strip() if args_match else ""
        handle_start(args)
    elif re.search(r"/custom-span-tracker:stop\b", prompt):
        handle_stop()

elif hook_event_name == "PostToolUse":
    skill = event.get("tool_input", {}).get("skill", "")
    args = event.get("tool_input", {}).get("args", "") or ""

    if skill == "custom-span-tracker:start":
        handle_start(args)
    elif skill == "custom-span-tracker:stop":
        handle_stop()

sys.exit(0)
