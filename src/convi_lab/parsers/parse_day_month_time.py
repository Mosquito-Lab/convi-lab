"""
parse_day_month_time.py: parses a day, a month name and a time, like "17 Jul - 02:00 PM".
"""

import re

from datetime import datetime

from convi_lab.conversions.convert_name import convert_name
from convi_lab.kernel.constants import MONTHS
from convi_lab.parsers.parser_handler import parser_handler
from convi_lab.kernel.logging_config import build_logger

logger = build_logger(__name__)


def parse_day_month_time(match: re.Match, today: datetime | None = None) -> datetime:
    """
    Convert a regex match from the ``day_month_time`` pattern into a ``datetime``.

    Match groups (in order):
    1. ``day``: day number, one or two digits (e.g. ``"17"``, ``"7"``)
    2. ``month``: month name or short form, any case (e.g. ``"Jul"``, ``"JULY"``, ``"Sept"``)
    3. ``time``: ``HH:MM`` string
    4. ``am_pm``: ``"AM"`` / ``"PM"`` / ``None``

    The month becomes its number through ``MONTHS``, so the result never
    depends on the locale. The year boundary rule applies (``resolve_date``).

    Args:
        match: ``re.Match`` produced by ``TIME_PATTERNS["day_month_time"]``.
        today: The moment to treat as now. ``None`` reads the clock once.
    Returns:
        The resolved ``datetime``.
    Raises:
        `DateComponentError`: when the day and month combination is invalid.
        `ClockFormatError`: when the time string cannot be parsed.
    Example::
        # Today is 2025-10-15
        parse_day_month_time(TIME_PATTERNS["day_month_time"].match("17Jan-02:00PM"))   # datetime(2026, 1, 17, 14, 0)
        parse_day_month_time(TIME_PATTERNS["day_month_time"].match("25Dec02:00"))      # datetime(2025, 12, 25, 2, 0)
    """

    day_str, month_str, time_str, am_pm = match.groups()
    logger.debug("Day: %s, Month: %s, Time: %s, AM/PM: %s", day_str, month_str, time_str, am_pm)

    # The pattern only admits real month spellings, so the match is exact
    month = MONTHS.index(convert_name(name=month_str, reference=MONTHS)) + 1

    return parser_handler(
        day=int(day_str), month=month, year=None, time_str=time_str, am_pm=am_pm,
        today=today if today is not None else datetime.now(),
    )
