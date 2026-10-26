"""
parse_datetime.py: parses numeric dates with a time, like "12/04 22:15" or "12.04.2025 10:15 PM".
"""

import re

from datetime import datetime

from convi_lab.kernel.utils import remove_spaces
from convi_lab.parsers.parser_handler import parser_handler
from convi_lab.kernel.logging_config import build_logger

logger = build_logger(__name__)


def parse_date_time(match: re.Match, today: datetime | None = None) -> datetime:
    """
    Convert a regex match from the ``datetime`` pattern into a ``datetime``.

    Match groups (in order):
    1. ``date``: day and month, ``dd/mm`` or ``dd.mm``, one or two digits each (e.g. ``"12/04"``)
    2. ``year``: optional 2- or 4-digit year, without its separator (e.g. ``"26"``, ``"2026"``, or ``None``)
    3. ``time``: ``HH:MM`` string
    4. ``am_pm``: ``"AM"`` / ``"PM"`` / ``None``

    A 2-digit year reads like ``strptime``'s ``%y``: ``00`` to ``68`` are
    2000 to 2068, ``69`` to ``99`` are 1969 to 1999. Without a year, the
    year boundary rule applies (``resolve_date``).

    Args:
        match: ``re.Match`` produced by ``TIME_PATTERNS["datetime"]``.
        today: The moment to treat as now. ``None`` reads the clock once.
    Returns:
        The resolved ``datetime``.
    Raises:
        `DateComponentError`: when the day, month or year can't make a real date.
        `ClockFormatError`: when the time string cannot be parsed.
    Example::
        # Today is 2026-05-13
        parse_date_time(TIME_PATTERNS["datetime"].match("17/07 22:15"))        # datetime(2026, 7, 17, 22, 15)
        parse_date_time(TIME_PATTERNS["datetime"].match("12.04.2025 08:00"))   # datetime(2025, 4, 12, 8, 0)
    """

    date_str, year_str, time_str, am_pm = match.groups()
    logger.debug("Day: %s, Year: %s, Time: %s, AM/PM: %s", date_str, year_str, time_str, am_pm)

    day, month = (int(part) for part in re.split(r"[./]", remove_spaces(date_str)))
    if year_str is None:
        year = None
    elif len(year_str) == 4:
        year = int(year_str)
    else:
        year = datetime.strptime(year_str, "%y").year

    return parser_handler(
        day=day, month=month, year=year, time_str=time_str, am_pm=am_pm,
        today=today if today is not None else datetime.now(),
    )
