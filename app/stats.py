"""Persist dashboard counters and a short recent-activity history."""

import os
import json
import threading
import datetime

STATS_PATH = os.environ.get("STATS_PATH", "/app/data/stats.json")
MAX_RECENT_EVENTS = 20

DEFAULT_STATS = {
    "movies_unmonitored": 0,
    "series_unmonitored": 0,
    "last_events": [],
}

_lock = threading.Lock()
_stats = None


def _load_from_disk():
    """Load saved statistics, filling in any keys missing from older files."""
    _ensure_storage_directory()
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, "r") as f:
            saved = json.load(f)
        stats = {**DEFAULT_STATS, **saved}
        stats["last_events"] = list(stats.get("last_events", []))
        return stats
    return {**DEFAULT_STATS, "last_events": []}


def _ensure_storage_directory():
    """Create the directory containing the statistics file when necessary."""
    directory = os.path.dirname(STATS_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _save_to_disk(s):
    """Write the current statistics dictionary to the configured JSON file."""
    _ensure_storage_directory()
    with open(STATS_PATH, "w") as f:
        json.dump(s, f, indent=2)


def init():
    """Load persisted statistics into the module's thread-safe state."""
    global _stats
    with _lock:
        _stats = _load_from_disk()


def get():
    """Return a shallow copy of the current dashboard statistics."""
    with _lock:
        return dict(_stats)


def record_unmonitor(kind, title):
    """Record one successful unmonitor operation and persist the new totals.

    Args:
        kind: Either ``"movie"`` or ``"series"``.
        title: Display title for the recent-activity entry.
    """
    with _lock:
        key = "movies_unmonitored" if kind == "movie" else "series_unmonitored"
        _stats[key] = _stats.get(key, 0) + 1

        event = {
            "kind": kind,
            "title": title,
            "at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        events = _stats.get("last_events", [])
        events.insert(0, event)
        _stats["last_events"] = events[:MAX_RECENT_EVENTS]

        _save_to_disk(_stats)


init()