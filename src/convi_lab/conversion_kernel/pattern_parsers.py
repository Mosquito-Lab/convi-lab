from logger_lab import lab
from datetime import datetime
from typing import Optional, Callable

from convi_lab.conversion_kernel.constants import TIME_PATTERNS
from convi_lab.parsers import parse_day_month_time, parse_day_time, parse_date_time

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)

# MAPS PATTERNS TO FUNCTIONS
_PATTERN_HANDLERS: dict[str, Callable] = {
    'day_time': parse_day_time,
    'day_month_time': parse_day_month_time,
    'datetime': parse_date_time,
}


# Match and parse pattern
def process_patterns(event_date: str) -> Optional[datetime]:
    """
    Try every pattern in ``TIME_PATTERNS`` against *event_date* in order,
    returning the first successful ``datetime`` parse.

    Note:
        All spaces must be removed from *event_date* before calling this
        function — use `remove_spaces()`.

    Args:
        event_date: Date/time string with all spaces already stripped.
    Returns:
        Parsed ``datetime`` on the first pattern match, or ``None`` if
        no pattern matches.
    """

    # Check each pattern till a match is found
    for pattern_name, pattern in TIME_PATTERNS.items():

        if match := pattern.match(event_date):

            handler = _PATTERN_HANDLERS[pattern_name]
            _date_time = handler(match)

            logger.debug(f"Matched pattern '{pattern_name}' for input '{event_date}'")

            return _date_time

    # Fallback
    return None
