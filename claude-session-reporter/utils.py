import json
import os
import sys
from pathlib import Path


DEFAULT_DIR = ".claude-sessions"
EVENTS_FILE = "all-events.jsonl"
FILTERED_EVENTS_FILE = "filtered-events.jsonl"


def _read_json(path: Path) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"])
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "claude-session-reporter"


def load_config() -> dict:
    return _read_json(_config_dir() / "config.json") or {}


def write_entry(path: Path, entry: dict) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def get_log_dir(config: dict) -> Path:
    """Return the directory where log files should be written.

    Defaults to DEFAULT_DIR in cwd; overridden by logs_base_dir in the config file.
    """
    base = config.get("logs_base_dir")
    if not base:
        log_dir = Path(DEFAULT_DIR)
        log_dir.mkdir(exist_ok=True)
        return log_dir

    base_dir = Path(base).expanduser()
    if not base_dir.is_absolute():
        raise ValueError(f"logs_base_dir must be an absolute path, got: {base!r}")
    cwd = Path.cwd()
    try:
        subdir = ".".join(cwd.relative_to(Path.home()).parts)
    except ValueError:
        subdir = ".".join(cwd.parts[1:])  # outside home: drop leading /

    log_dir = base_dir / subdir
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
