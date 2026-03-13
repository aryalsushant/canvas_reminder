"""
config.py — Loads and validates configuration from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    """Fetch a required env var, raising an error if it's missing."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


# Canvas
CANVAS_API_URL: str = _require("CANVAS_API_URL").rstrip("/")
CANVAS_API_TOKEN: str = _require("CANVAS_API_TOKEN")

# Telegram
TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str = _require("TELEGRAM_CHAT_ID")

# Behaviour
REMINDER_HOURS_BEFORE: float = float(os.getenv("REMINDER_HOURS_BEFORE", "3"))
CHECK_INTERVAL_MINUTES: float = float(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
TIMEZONE: str = os.getenv("TIMEZONE", "UTC")

# Optional: comma-separated course IDs, e.g. "12345,67890"
_course_ids_raw: str = os.getenv("CANVAS_COURSE_IDS", "")
CANVAS_COURSE_IDS: list[int] = (
    [int(cid.strip()) for cid in _course_ids_raw.split(",") if cid.strip()]
    if _course_ids_raw.strip()
    else []
)
