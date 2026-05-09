import re

from datetime import datetime
from logger_lab.main import lab

from convi_lab.conversions.convert_name import convert_name
from convi_lab.conversion_kernel.constants import MONTHS, TEST_CASES
from convi_lab.conversion_kernel.utils import match_pattern, parser_handler
from convi_lab.conversion_kernel.errors import MonthResolutionError, DateComponentError

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)

# Date Month Time: "17Jan-02:00PM", "25Dec02:00", "03Jul-14:30am"
def parse_day_month_time(match: re.Match) -> datetime:
    """
    Convert a regex match from the ``day_month_time`` pattern into a ``datetime``.

    Match groups (in order):
    1. ``day``    — two-digit day number (e.g. ``"17"``)
    2. ``month``  — abbreviated or full month name (e.g. ``"Jul"``, ``"July"``)
    3. ``time``   — ``HH:MM`` string
    4. ``am_pm``  — ``"AM"`` / ``"PM"`` / ``None``

    Year boundary rule: if the resolved date is already in the past (date only,
    ignoring time), the year is bumped to the next calendar year.

    Examples (assuming today is 2025-10-15):
        "17Jan-02:00PM"  → 2026-01-17 14:00:00  (January already passed)
        "25Dec02:00"     → 2025-12-25 02:00:00  (December still ahead)
    Args:
        match: ``re.Match`` produced by ``TIME_PATTERNS["day_month_time"]``.
    Returns:
        Parsed and potentially year-corrected ``datetime``.
    Raises:
        MonthResolutionError:
            If the month string cannot be resolved.
        DateComponentError:
            If the day+month combination is invalid.
        ClockFormatError:
            If the time string cannot be parsed.
    """

    day_str, month_str, time_str, am_pm = match.groups()
    logger.debug(f'Day: {day_str}, Month: {month_str}, Time: {time_str}, AM/PM: {am_pm}')

    # Resolve month abbreviation → full name; raises FuzzyMatchError on failure.
    # Re-raise as MonthResolutionError so callers see a parser-domain error.
    _month = convert_name(month_str, MONTHS)
    if not _month:
        raise MonthResolutionError(month_str)

    # Handle date object
    try:
        current_year = datetime.now().year
        date_object = datetime.strptime(f"{day_str}.{_month}.{current_year}", "%d.%B.%Y")

    except ValueError as e:
        raise DateComponentError(f"{day_str}/{_month}", str(e)) from e

    return parser_handler(date_object=date_object, time_str=time_str, am_pm=am_pm)


# Example usage and test case
def _test_case():
    """ Tests processing of the datetime patterns. """

    for case in TEST_CASES:
        try:
            logger.debug(
                f"Input: {case}, Output: {parse_day_month_time(match_pattern('day_month_time', case))}"
            )

        except (ValueError, KeyError, AttributeError):

            continue


if __name__ == '__main__':
    # TEST
    _test_case()
