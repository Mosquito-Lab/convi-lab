"""
process_patterns.py: tries each pattern in ``TIME_PATTERNS`` and hands the first match to its parser.
"""

from collections.abc import Callable
from datetime import datetime

from convi_lab.kernel.constants import TIME_PATTERNS
from convi_lab.kernel.logging_config import build_logger
from convi_lab.parsers.parse_day_month_time import parse_day_month_time
from convi_lab.parsers.parse_day_time import parse_day_time
from convi_lab.parsers.parse_datetime import parse_date_time

logger = build_logger(__name__)

# The parser for each pattern in TIME_PATTERNS, by the same name (a test keeps the keys equal)
PATTERN_HANDLERS: dict[str, Callable[..., datetime]] = {  # Each is called as (match, today=...)
    'day_time': parse_day_time,
    'day_month_time': parse_day_month_time,
    'datetime': parse_date_time,
}


def process_patterns(event_date: str) -> datetime | None:
    """
    Try every pattern in ``TIME_PATTERNS`` against *event_date* in order,
    returning the first successful ``datetime`` parse.

    Unlike ``convert_date_time()``, this lets the parsers' typed errors through.

    Note: whitespace between the parts is optional, so spaced and compact
    input both work. Leading and trailing whitespace must be trimmed first.

    Args:
        event_date: Date/time string, trimmed at both ends.
    Returns:
        Parsed ``datetime`` on the first pattern match, or ``None`` if
        no pattern matches.
    Raises:
        `ParserError`: when a matched part can't be resolved (``DateComponentError``).
        `ClockFormatError`: when the matched time can't be parsed.
    Example::
        process_patterns("17 Jul - 02:00 PM")   # datetime(2026, 7, 17, 14, 0), when run before July 17, 2026
    """

    # Check each pattern till a match is found
    for pattern_name, pattern in TIME_PATTERNS.items():
        if match := pattern.match(event_date):
            logger.debug("Matched pattern '%s' for input '%s'", pattern_name, event_date)
            return PATTERN_HANDLERS[pattern_name](match, today=datetime.now())  # The one clock read for this conversion

    return None
