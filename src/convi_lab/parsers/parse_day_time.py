"""
parse_day_time.py: parses a day name and a time, like "Tuesday 12:30" or "Today 14:30".
"""

import re

from datetime import datetime, timedelta

from convi_lab.conversions.convert_name import convert_name
from convi_lab.parsers.parser_handler import parser_handler
from convi_lab.kernel.constants import DAYS, WEEKDAY_MAP
from convi_lab.kernel.logging_config import build_logger

logger = build_logger(__name__)


def next_weekday(day: str, today: datetime) -> datetime:
    """
    Resolve a full weekday name to the **next** occurrence of that weekday.

    If today is the target weekday, the result is pushed one week ahead so the
    return value is always strictly in the future.

    Args:
        day: Full weekday name, e.g. ``"Monday"`` (a key of ``WEEKDAY_MAP``).
        today: The moment to count from.
    Returns:
        A ``datetime`` on the next occurrence of *day*.
    """

    # Calculate days ahead (always next occurrence, min 1 day)
    days_ahead = (WEEKDAY_MAP[day] - today.weekday() + 7) % 7

    if days_ahead == 0:
        days_ahead = 7  # Always push to the *next* occurrence

    return today + timedelta(days=days_ahead)


def relative_day(day: str, today: datetime) -> datetime:
    """
    Resolve ``"Today"`` or ``"Tomorrow"`` to a concrete date.

    Args:
        day: ``"Today"`` or ``"Tomorrow"``.
        today: The moment to count from.
    Returns:
        A ``datetime`` on the given relative day.
    """

    return today if day == "Today" else today + timedelta(days=1)


def parse_day_time(match: re.Match, today: datetime | None = None) -> datetime:
    """
    Convert a regex match from the ``day_time`` pattern into a ``datetime``.

    Match groups (in order):
    1. ``day``: day name or short form, any case
       (e.g. ``"Mon"``, ``"Tues"``, ``"monday"``, ``"Today"``, ``"Tomorrow"``)
    2. ``time``: ``HH:MM`` string
    3. ``am_pm``: ``"AM"`` / ``"PM"`` / ``None``

    Short forms are expanded to their full names via fuzzy matching. The
    pattern only admits real spellings, so the match is exact.

    Args:
        match: ``re.Match`` produced by ``TIME_PATTERNS["day_time"]``.
        today: The moment to treat as now. ``None`` reads the clock once.
    Returns:
        ``datetime`` for the resolved day and time.
    Raises:
        `ClockFormatError`: when the time string cannot be parsed.
    Example::
        # Today is Wednesday 2026-05-13
        parse_day_time(TIME_PATTERNS["day_time"].match("Monday12:30PM"))   # datetime(2026, 5, 18, 12, 30)
        parse_day_time(TIME_PATTERNS["day_time"].match("Today09:00am"))    # datetime(2026, 5, 13, 9, 0)
    """

    day_str, time_str, am_pm = match.groups()
    logger.debug("Day: %s, Time: %s, AM/PM: %s", day_str, time_str, am_pm)

    today = today if today is not None else datetime.now()

    # Parse day (handles short forms and standard forms: Wed to Wednesday)
    day = convert_name(name=day_str, reference=DAYS)
    date_object = next_weekday(day, today) if day in WEEKDAY_MAP else relative_day(day, today)

    return parser_handler(
        day=date_object.day, month=date_object.month, year=date_object.year,
        time_str=time_str, am_pm=am_pm, today=today,
    )
