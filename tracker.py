"""
tracker.py — Persists which reminders have already been sent to avoid duplicates.

Storage format (sent_reminders.json):
{
    "<assignment_id>_<reminder_window_hours>h": "2024-03-15T10:30:00+00:00",
    ...
}
The value is the ISO timestamp of when the reminder was sent (for auditing).
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from canvas_client import Assignment

logger = logging.getLogger(__name__)

_STORAGE_FILE = Path("sent_reminders.json")


def _load() -> dict[str, str]:
    """Load the persisted reminder log from disk."""
    if not _STORAGE_FILE.exists():
        return {}
    try:
        return json.loads(_STORAGE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s: %s — starting fresh", _STORAGE_FILE, exc)
        return {}


def _save(data: dict[str, str]) -> None:
    """Write the reminder log back to disk."""
    try:
        _STORAGE_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.error("Could not write %s: %s", _STORAGE_FILE, exc)


def _key(assignment: Assignment, reminder_hours: float) -> str:
    """
    Build a unique key for this assignment + reminder window combination.
    Using hours as an integer label keeps keys readable and stable.
    """
    return f"{assignment.id}_{reminder_hours}h"


def already_sent(assignment: Assignment, reminder_hours: float) -> bool:
    """Return True if a reminder has already been sent for this assignment."""
    data = _load()
    return _key(assignment, reminder_hours) in data


def mark_sent(assignment: Assignment, reminder_hours: float) -> None:
    """Record that a reminder has been sent for this assignment."""
    data = _load()
    data[_key(assignment, reminder_hours)] = datetime.now(timezone.utc).isoformat()
    _save(data)
    logger.debug("Marked reminder sent: %s", _key(assignment, reminder_hours))


def cleanup_past(assignments: list[Assignment]) -> None:
    """
    Remove entries for assignments whose due dates are now in the past.
    This keeps sent_reminders.json from growing indefinitely.
    """
    now = datetime.now(timezone.utc)
    due_by_id = {a.id: a.due_at for a in assignments}

    data = _load()
    before = len(data)

    # Extract the assignment ID from the key (format: "<id>_<hours>h")
    def is_past(key: str) -> bool:
        try:
            assignment_id = int(key.split("_")[0])
        except (ValueError, IndexError):
            return False
        due_at = due_by_id.get(assignment_id)
        # If the assignment is no longer in the upcoming list, it's past due
        return due_at is None or due_at < now

    data = {k: v for k, v in data.items() if not is_past(k)}

    if len(data) < before:
        logger.info("Cleaned up %d past reminder entries", before - len(data))
        _save(data)
