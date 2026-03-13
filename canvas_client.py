"""
canvas_client.py — Fetches upcoming assignments from the Canvas LMS API.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests

import config

logger = logging.getLogger(__name__)


@dataclass
class Assignment:
    id: int
    name: str
    course_name: str
    due_at: datetime          # always UTC-aware
    html_url: str


def _get_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {config.CANVAS_API_TOKEN}"}


def _paginate(url: str, params: Optional[dict] = None) -> list[dict]:
    """Follow Canvas pagination (Link header) and collect all results."""
    results: list[dict] = []
    while url:
        response = requests.get(url, headers=_get_headers(), params=params, timeout=30)
        response.raise_for_status()
        results.extend(response.json())

        # After the first request params are embedded in the next URL, so clear them.
        params = None

        # Parse the Link header for the next page
        link_header = response.headers.get("Link", "")
        url = _parse_next_link(link_header)

    return results


def _parse_next_link(link_header: str) -> Optional[str]:
    """Extract the 'next' URL from a Canvas Link header, or return None."""
    if not link_header:
        return None
    for part in link_header.split(","):
        section = part.strip().split(";")
        if len(section) == 2 and 'rel="next"' in section[1]:
            return section[0].strip().strip("<>")
    return None


def _parse_due_at(due_at_str: str) -> datetime:
    """Parse an ISO 8601 UTC timestamp from Canvas into an aware datetime."""
    # Canvas always returns UTC, indicated by the trailing 'Z'
    return datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))


def get_active_course_ids() -> list[int]:
    """Return a list of course IDs for all currently active enrollments."""
    url = f"{config.CANVAS_API_URL}/api/v1/courses"
    params = {"enrollment_state": "active", "per_page": 100}
    courses = _paginate(url, params)
    ids = [c["id"] for c in courses if isinstance(c.get("id"), int)]
    logger.info("Found %d active courses", len(ids))
    return ids


def get_course_name(course_id: int) -> str:
    """Fetch the human-readable name for a single course."""
    url = f"{config.CANVAS_API_URL}/api/v1/courses/{course_id}"
    try:
        response = requests.get(url, headers=_get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("name", f"Course {course_id}")
    except requests.RequestException as exc:
        logger.warning("Could not fetch course name for %d: %s", course_id, exc)
        return f"Course {course_id}"


def get_upcoming_assignments() -> list[Assignment]:
    """
    Return all upcoming assignments (with a due date) across the configured
    courses.  Results are sorted by due date ascending.
    """
    course_ids = config.CANVAS_COURSE_IDS or get_active_course_ids()

    assignments: list[Assignment] = []
    for course_id in course_ids:
        try:
            course_name = get_course_name(course_id)
            url = f"{config.CANVAS_API_URL}/api/v1/courses/{course_id}/assignments"
            params = {"order_by": "due_at", "bucket": "upcoming", "per_page": 50}
            raw = _paginate(url, params)

            for item in raw:
                due_at_str: Optional[str] = item.get("due_at")
                if not due_at_str:
                    continue  # skip assignments with no due date

                assignments.append(
                    Assignment(
                        id=item["id"],
                        name=item.get("name", "Untitled Assignment"),
                        course_name=course_name,
                        due_at=_parse_due_at(due_at_str),
                        html_url=item.get("html_url", ""),
                    )
                )
            logger.debug(
                "Fetched %d upcoming assignments for course %d (%s)",
                len(raw),
                course_id,
                course_name,
            )
        except requests.RequestException as exc:
            logger.error("Error fetching assignments for course %d: %s", course_id, exc)
            continue

    assignments.sort(key=lambda a: a.due_at)
    return assignments
