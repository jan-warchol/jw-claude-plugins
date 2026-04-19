#!/usr/bin/env python3
"""Shared utilities for custom-span-tracker hooks."""

import json
import sys
from pathlib import Path

SPANS_DIR = Path(".debug")
CURRENT_DIR = SPANS_DIR / "current"
SPAN_INFO_FILE = CURRENT_DIR / "span-info.json"


def load_event():
    return json.load(sys.stdin)


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def load_active_span():
    """Return active span dict, or None if no span is currently running."""
    if not SPAN_INFO_FILE.exists():
        return None
    data = read_json(SPAN_INFO_FILE)
    return data if data.get("span_id") else None
