#!/usr/bin/env python3
import json
import sys
import time
from utils import EVENTS_FILE, get_log_dir, load_config, write_entry

if __name__ == "__main__":
    event = json.load(sys.stdin)
    entry = {"timestamp": int(time.time()), **event}

    config = load_config()
    log_dir = get_log_dir(config)
    write_entry(log_dir / EVENTS_FILE, entry)
