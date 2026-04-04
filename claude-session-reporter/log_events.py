#!/usr/bin/env python3
import json
import sys
import time
from utils import get_log_dir, load_config, write_entry

FILE_NAME = "all-events.jsonl"
DEFAULT_DIR = "./.claude-sessions"

if __name__ == "__main__":
    # Add timestamp and move subagent info to the end for better readability.
    event = json.load(sys.stdin)
    TAIL_KEYS = ("agent_id", "agent_type")
    tail = {k: event.pop(k) for k in TAIL_KEYS if k in event}
    entry = {"timestamp": int(time.time()), **event, **tail}

    config = load_config()
    log_dir = get_log_dir(config, DEFAULT_DIR)
    write_entry(log_dir / FILE_NAME, entry)
