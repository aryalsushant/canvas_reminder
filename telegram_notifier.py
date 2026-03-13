"""
telegram_notifier.py — Sends reminder messages via the Telegram Bot API.
"""

import logging
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import config
from canvas_client import Assignment

logger = logging.getLogger(__name__)

_TELEGRAM_API = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"

# Characters that must be escaped in Telegram MarkdownV2
_ESCAPE_CHARS = r"\_*[]()~`>#+-=|{}.!"


def _escape(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    return re.sub(r"([" + re.escape(_ESCAPE_CHARS) + r"])", r"\\\1", text)


def _humanize_due(due_at: datetime) -> str:
    """
    Return a friendly due-date string relative to now, e.g.
    'Today at 11:59 PM' or 'Tomorrow at 3:00 PM'.
    Times are converted to the configured TIMEZONE for display.
    """
    tz = ZoneInfo(config.TIMEZONE)
    local_due = due_at.astimezone(tz)
    local_now = datetime.now(timezone.utc).astimezone(tz)

    due_date = local_due.date()
    today = local_now.date()

    time_str = local_due.strftime("%-I:%M %p")  # e.g. "3:00 PM"

    if due_date == today:
        return f"Today at {time_str}"
    elif due_date == today.replace(day=today.day + 1) or (due_date - today).days == 1:
        return f"Tomorrow at {time_str}"
    else:
        return local_due.strftime("%A, %b %-d at %-I:%M %p")  # "Monday, Mar 4 at 3:00 PM"


def _time_remaining(due_at: datetime) -> str:
    """Return a human-readable string for time remaining, e.g. '2 hours 30 minutes'."""
    now = datetime.now(timezone.utc)
    delta = due_at - now
    total_minutes = int(delta.total_seconds() / 60)

    if total_minutes < 1:
        return "less than a minute"

    hours, minutes = divmod(total_minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return " ".join(parts)


def _build_message(assignment: Assignment) -> str:
    """Compose the MarkdownV2-formatted reminder message."""
    name = _escape(assignment.name)
    course = _escape(assignment.course_name)
    due_str = _escape(_humanize_due(assignment.due_at))
    remaining = _escape(_time_remaining(assignment.due_at))
    url = assignment.html_url  # URLs don't need general escaping inside []()

    return (
        f"🔔 *Assignment Reminder*\n\n"
        f"📝 *{name}*\n"
        f"📚 {course}\n"
        f"⏰ Due: {due_str}\n"
        f"⌛ Time remaining: {remaining}\n\n"
        f"[View Assignment]({url})"
    )


def send_reminder(assignment: Assignment) -> bool:
    """
    Send a Telegram reminder for the given assignment.
    Returns True on success, False on failure.
    """
    message = _build_message(assignment)
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(
            f"{_TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        logger.info("Reminder sent for '%s'", assignment.name)
        return True
    except requests.HTTPError as exc:
        # Log the actual Telegram error body for easier debugging
        logger.error(
            "Telegram API error for '%s': %s — %s",
            assignment.name,
            exc,
            exc.response.text if exc.response is not None else "",
        )
        return False
    except requests.RequestException as exc:
        logger.error("Failed to send Telegram message for '%s': %s", assignment.name, exc)
        return False
