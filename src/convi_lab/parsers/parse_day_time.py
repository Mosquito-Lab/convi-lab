import re

from logger_lab import lab
from datetime import datetime, timedelta

from convi_lab.conversion_kernel.errors import DayResolutionError
from convi_lab.conversions.convert_name import convert_name
from convi_lab.conversion_kernel.utils import match_pattern, parser_handler
from convi_lab.conversion_kernel.constants import DAYS, RELATIVE_DAYS, WEEKDAY_MAP

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)

# Weekday : a day in the current (Wednesday, Thursday, Friday)
def _parse_weekday(day: str) -> datetime:
    """
    Resolve a full weekday name to the **next** occurrence of that weekday.

    If today is the target weekday, the result is pushed one week ahead so the
    return value is always strictly in the future.

    Args:
        day:   Full weekday name, e.g. ``"Monday"`` (must be in ``WEEKDAY_MAP``).
    Returns:
        ``date_object`` for the next occurrence of *day*.
    Raises:
        DayResolutionError:
            If *day* is not in ``WEEKDAY_MAP``.
    """

    if day not in WEEKDAY_MAP:
        raise DayResolutionError(day)

    current_datetime = datetime.now()
    current_weekday = current_datetime.weekday()
    target_weekday = WEEKDAY_MAP[day]

    # Calculate days ahead (always next occurrence, min 1 day)
    days_ahead = (target_weekday - current_weekday + 7) % 7

    if days_ahead == 0:
        days_ahead = 7  # Always push to the *next* occurrence

    return current_datetime + timedelta(days=days_ahead)


# Relative time: the time Today or Tomorrow
def _parse_relative(day: str) -> datetime:
    """
    Resolve ``"Today"`` or ``"Tomorrow"`` to a concrete ``date_object``.

    Args:
        day:   ``"Today"`` or ``"Tomorrow"``.
    Returns:
        ``date_object`` for the given relative day.
    Raises:
        DayResolutionError:
            If *day* is neither ``"Today"`` nor ``"Tomorrow"``.
    """

    if day == "Today":
        return datetime.now()

    elif day == "Tomorrow":
        return datetime.now() + timedelta(days=1)

    else:
        raise DayResolutionError(day)


# Day time pattern:  "Mon12:30", "Monday01:15PM", "Tomorrow22:00", "Today06:30AM"
def parse_day_time(match: re.Match) -> datetime:
    """
    Convert a regex match from the ``day_time`` pattern into a ``datetime``.

    Match groups (in order):
    1. ``day``    — day identifier, abbreviated or full
                    (e.g. ``"Mon"``, ``"Monday"``, ``"Today"``, ``"Tomorrow"``)
    2. ``time``   — ``HH:MM`` string
    3. ``am_pm``  — ``"AM"`` / ``"PM"`` / ``None``

    Abbreviated names (``"Mon"``, ``"Tue"`` …) are expanded to their full
    forms via fuzzy matching before dispatch.

    Examples:
        "Monday12:30PM" -> Next Monday at 12:30 PM
        "Tue14:30" -> Next Tuesday at 14:30 (2:30 PM)
        "Today09:00am" -> Today at 09:00 AM
        "Tomorrow15:45" -> Tomorrow at 15:45 (3:45 PM)
    Args:
        match: ``re.Match`` produced by ``TIME_PATTERNS["day_time"]``.
    Returns:
        ``datetime`` for the resolved day and time.
    Raises:
        DayResolutionError:
            If the day identifier cannot be resolved.
        ClockFormatError:
            If the time string cannot be parsed.
    """

    day_str, time_str, am_pm = match.groups()
    logger.debug(f'Day: {day_str}, Time: {time_str}, AM/PM: {am_pm}')

    # Parse day (handles short forms and standard forms: Wed to Wednesday)
    _day = convert_name(day_str, DAYS)

    if _day in RELATIVE_DAYS:
        return parser_handler(
            date_object=_parse_relative(_day),
            time_str=time_str, am_pm=am_pm
        )

    elif _day in WEEKDAY_MAP:
        return parser_handler(
            date_object=_parse_weekday(_day),
            time_str=time_str, am_pm=am_pm
        )

    else:
        raise DayResolutionError(day_str)


# Example usage and test case
def _test_case():
    """ Tests processing of the day patterns. """

    test_cases = ["Mon12:30", "Monday01:15PM", "Tomorrow22:00", "Today06:30AM"]

    for case in test_cases:
        try:
            logger.debug(
                f"Input: {case}, Output: {parse_day_time(match_pattern('day_time', case))}"
            )

        except (ValueError, KeyError, AttributeError):

            continue


if __name__ == '__main__':
    # TEST
    _test_case()
