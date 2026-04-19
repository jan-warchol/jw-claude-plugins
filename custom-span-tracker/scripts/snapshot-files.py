#!/usr/bin/env python3
"""
Save timestamped snapshots of tracked markdown files on every agent Edit or Write.

A .md file is snapshotted if "plan", "spec", or "review" appears anywhere in
its path relative to the project root (including the filename itself).
Snapshots are saved to .debug/current/snapshots/<stem>_<timestamp><ext>.
"""

import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import utils

KEYWORDS = {"plan", "spec", "review"}


def is_tracked(file_path: Path, cwd: Path) -> bool:
    if file_path.suffix.lower() != ".md":
        return False
    try:
        rel = file_path.relative_to(cwd) if file_path.is_absolute() else file_path
    except ValueError:
        rel = file_path
    path_lower = str(rel).lower()
    return any(kw in path_lower for kw in KEYWORDS)


event = utils.load_event()
tool_input = event.get("tool_input", {})
file_path = Path(tool_input.get("file_path", ""))
cwd = Path(event.get("cwd", "."))

if not file_path.name or not is_tracked(file_path, cwd):
    sys.exit(0)

if not file_path.exists():
    sys.exit(0)

if not utils.load_active_span():
    sys.exit(0)

ts = int(time.time())
shutil.copy2(file_path, utils.CURRENT_DIR / f"{file_path.stem}_{ts}{file_path.suffix}")

sys.exit(0)
