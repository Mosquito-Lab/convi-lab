"""
parser_handler.py: the last step every parser shares.

It resolves the date with the year boundary rule and joins it with the time.
"""

from datetime import datetime

from convi_lab.conversions.convert_clock_format import convert_to_24_format
from convi_lab.kernel.errors import DateComponentError
from convi_lab.kernel.utils import remove_spaces

YEARS_TO_SEARCH = 9  # Nine years always hold the next Feb 29, even across 2100 (2097 to 2104)


def resolve_date(day: int, month: int, year: int | None, today: datetime) -> datetime:
    """
    Return the date a day and month stand for.

    Year boundary rule: with a *year*, the date is exactly that day, even in
    the past. Without one, it is the next occurrence on or after *today*'s
    date. A date already past this year is next year's, and February 29 is
    the next leap year's.

    Args:
        day: Day of the month, 1 to 31.
        month: Month number, 1 to 12.
        year: The year the input gave, or ``None``.
        today: The moment the conversion treats as now.
    Returns:
        The date, at midnight.
    Raises:
        `DateComponentError`: when no year makes it a real date (``31/04``),
        or the given year doesn't (``29/02/2027``).
    Example::
        resolve_date(day=17, month=1, year=None, today=datetime(2026, 5, 13))   # datetime(2027, 1, 17)
        resolve_date(day=29, month=2, year=None, today=datetime(2026, 5, 13))   # datetime(2028, 2, 29)
    """

    years = [year] if year is not None else range(today.year, today.year + YEARS_TO_SEARCH)
    reason = ""

    for candidate in years:
        try:
            date_object = datetime(candidate, month, day)

        except ValueError as e:
            reason = str(e)
            continue

        if year is not None or date_object.date() >= today.date():
            return date_object

    fragment = f"{day:02d}.{month:02d}" if year is None else f"{day:02d}.{month:02d}.{year}"
    raise DateComponentError(fragment=fragment, reason=reason)


def parser_handler(
    day: int, month: int, year: int | None, time_str: str, am_pm: str | None, today: datetime
) -> datetime:
    """
    Resolve a parser's date with the year boundary rule, then join it with its time.

    Every parser ends here, so the rule lives in one place (``resolve_date``).

    Args:
        day: Day of the month.
        month: Month number.
        year: The year the input gave, or ``None``.
        time_str: ``HH:MM`` string, possibly with whitespace around the colon.
        am_pm: ``"AM"`` / ``"PM"`` / ``None``.
        today: The moment the conversion treats as now. Read once per conversion.
    Returns:
        The resolved ``datetime``.
    Raises:
        `DateComponentError`: when the day and month don't make a real date.
        `ClockFormatError`: when *time_str* cannot be parsed.
    Example::
        parser_handler(day=17, month=7, year=None, time_str="02:00", am_pm="PM", today=datetime(2026, 5, 13))
        # datetime(2026, 7, 17, 14, 0)
    """

    date_object = resolve_date(day=day, month=month, year=year, today=today)
    time_object = convert_to_24_format(time=remove_spaces(time_str), am_pm=am_pm)

    return datetime.combine(date_object.date(), time_object.time())
