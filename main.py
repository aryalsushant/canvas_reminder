"""
main.py — Entry point for the Canvas Assignment Reminder Bot.

Run with:  python main.py
"""

import logging
import time
from datetime import datetime, timezone

import config
import canvas_client
import telegram_notifier
import tracker

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def is_within_reminder_window(due_at: datetime, hours_before: float) -> bool:
    """
    Return True if the assignment is due within `hours_before` hours from now
    and is not already past due.
    """
    now = datetime.now(timezone.utc)
    seconds_until_due = (due_at - now).total_seconds()
    window_seconds = hours_before * 3600

    return 0 < seconds_until_due <= window_seconds


def run_check() -> None:
    """
    Single check cycle:
      1. Fetch upcoming assignments from Canvas.
      2. For each one, decide whether a reminder should be sent.
      3. Send via Telegram and persist the record.
      4. Clean up stale tracker entries.
    """
    logger.info("Checking for upcoming assignments…")

    try:
        assignments = canvas_client.get_upcoming_assignments()
    except Exception as exc:
        logger.error("Failed to fetch assignments from Canvas: %s", exc)
        return

    logger.info("Found %d upcoming assignment(s)", len(assignments))

    for assignment in assignments:
        try:
            if not is_within_reminder_window(assignment.due_at, config.REMINDER_HOURS_BEFORE):
                continue

            if tracker.already_sent(assignment, config.REMINDER_HOURS_BEFORE):
                logger.debug(
                    "Reminder already sent for '%s' (id=%d)", assignment.name, assignment.id
                )
                continue

            logger.info(
                "Sending reminder for '%s' due at %s",
                assignment.name,
                assignment.due_at.isoformat(),
            )
            success = telegram_notifier.send_reminder(assignment)
            if success:
                tracker.mark_sent(assignment, config.REMINDER_HOURS_BEFORE)

        except Exception as exc:
            logger.error(
                "Unexpected error processing assignment '%s' (id=%d): %s",
                assignment.name,
                assignment.id,
                exc,
            )
            continue

    # Clean up tracker entries for assignments that are now past due
    try:
        tracker.cleanup_past(assignments)
    except Exception as exc:
        logger.warning("Tracker cleanup failed: %s", exc)


def main() -> None:
    interval_seconds = config.CHECK_INTERVAL_MINUTES * 60

    logger.info(
        "Canvas Reminder Bot started. "
        "Checking every %.0f minute(s), reminding %.1f hour(s) before due dates.",
        config.CHECK_INTERVAL_MINUTES,
        config.REMINDER_HOURS_BEFORE,
    )

    while True:
        run_check()
        logger.info("Next check in %.0f minute(s).", config.CHECK_INTERVAL_MINUTES)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
