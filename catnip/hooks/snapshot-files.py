#!/usr/bin/env python3
"""
Save timestamped snapshots of tracked markdown files on every agent Edit or Write.

A .md file is snapshotted if "plan", "spec", or "review" appears anywhere in
its path relative to the project root (including the filename itself).
Snapshots are saved to .debug/<stem>_<timestamp><ext>.
"""

import shutil
import sys
import time
import json
from pathlib import Path

KEYWORDS = {"plan", "spec", "review"}
FILENAMES = {".catnip-task-complexity.json"}
SNAPSHOTS_DIR = Path(".debug")


def load_event() -> dict:
    return json.load(sys.stdin)


def is_tracked(file_path: Path, cwd: Path) -> bool:
    if file_path.name in FILENAMES:
        return True
    if file_path.suffix.lower() != ".md":
        return False
    try:
        rel = file_path.relative_to(cwd) if file_path.is_absolute() else file_path
    except ValueError:
        rel = file_path
    path_lower = str(rel).lower()
    return any(kw in path_lower for kw in KEYWORDS)


event = load_event()
tool_input = event.get("tool_input", {})
file_path = Path(tool_input.get("file_path", ""))
cwd = Path(event.get("cwd", "."))

if not file_path.name or not is_tracked(file_path, cwd):
    sys.exit(0)

if not file_path.exists():
    sys.exit(0)

SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
ts = int(time.time())
shutil.copy2(file_path, SNAPSHOTS_DIR / f"{ts}_{file_path.name}")

sys.exit(0)
