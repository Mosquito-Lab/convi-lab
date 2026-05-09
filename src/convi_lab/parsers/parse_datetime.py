import re

from logger_lab import lab
from typing import Optional
from datetime import datetime

from convi_lab.conversion_kernel.constants import TEST_CASES
from convi_lab.conversion_kernel.errors import DateComponentError
from convi_lab.conversion_kernel.utils import match_pattern, parser_handler

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)


# Date: "12/08", "12.04.2025", "31/12/25"
def _parse_date(date: str, year: Optional[str] = None) -> datetime:
    """
    Build a ``datetime`` from a ``dd/mm`` or ``dd.mm`` fragment plus an
    optional year suffix.

    Args:
        date: Day and month in ``dd/mm`` or ``dd.mm`` format. (e.g., "23/10", "24/09", "25.08")
        year: Year suffix in ``/yy``, ``/yyyy``, ``.yy``, or ``.yyyy`` form,
                 or ``None`` to use the current year. (e.g., "25", "2025")
    Returns:
        date object with the complete parsed date
    Raises:
         DateComponentError:
            On any unrecognised year fragment or strptime() failure.
    """

    normalised_date = date.replace("/", ".")  # Unify separators

    try:
        if year is None:
            logger.debug(f"Parsing '{normalised_date}' with no year specified")
            full = f"{normalised_date}.{datetime.now().year}"

            return datetime.strptime(full, "%d.%m.%Y")

        # Handle year logic
        normalised_year = year.replace("/", ".")
        if len(normalised_year) == 3:  # ".yy"
            logger.debug(f"Handling '.yy': {normalised_year}")

            return datetime.strptime(f"{normalised_date}{normalised_year}", "%d.%m.%y")

        elif len(normalised_year) == 5:  # ".yyyy"
            logger.debug(f"Handling '.yyyy': {normalised_year}")

            return datetime.strptime(f"{normalised_date}{normalised_year}", "%d.%m.%Y")

        else:
            raise DateComponentError(year, "year fragment must be 2 or 4 digits")

    except DateComponentError:
        raise

    except ValueError as e:
        raise DateComponentError(
            date if year is None else f"{date}{year}", str(e)
        ) from e


# Date time: "12/0804:20AM", "12.04.202512:15pm", "31/12/2523:59"
def parse_date_time(match: re.Match) -> datetime:
    """
    Convert a regex match from the ``datetime`` pattern into a ``datetime``.

    Match groups (in order):
    1. ``date``   — day/month in ``dd/mm`` or ``dd.mm`` form (e.g. ``"12/04"``)
    2. ``year``   — optional year suffix  (e.g. ``"/25"``, ``".2025"``, or ``None``)
    3. ``time``   — ``HH:MM`` string
    4. ``am_pm``  — ``"AM"`` / ``"PM"`` / ``None``

    Examples:
        "12.04.202512:15pm" -> April 12, 2025 12:15:00
        "31/12/202423:59" -> December 31, 2024 23:59:00
        "01.01.202600:00AM" -> January 1, 2026 00:00:00
        "12/0422:15" -> April 12, 2025 22:15:00
        "31/1210:30PM" -> December 31, 2025 22:30:00
        "05/0608:00am" -> June 5, 2025 08:00:00

    Year boundary rule: if the resolved date is in the past (date only, ignoring
    time), the year is bumped to the following calendar year.

    Args:
        match: ``re.Match`` produced by ``TIME_PATTERNS["datetime"]``.
    Returns:
        Parsed and potentially year-corrected ``datetime``.
    Raises:
        ClockFormatError:
            If the time string cannot be parsed.
    """

    date_str, year_str, time_str, am_pm = match.groups()
    logger.debug(f" Day: {date_str} Year: {year_str} Time: {time_str} AM/PM: {am_pm}")

    # Parse date (handle both . and / separators)
    _date = str(date_str.replace('/', '.'))

    date_object = _parse_date(_date, year_str)  # Normalized date

    return parser_handler(date_object=date_object, time_str=time_str, am_pm=am_pm)


# Example usage and test case
def _test_case():
    """ Tests processing of the datetime patterns. """

    for case in TEST_CASES:
        try:
            logger.debug(
                f"Input: {case}, Output: {parse_date_time(match_pattern('datetime', case))}"
            )

        except (ValueError, KeyError, AttributeError) :
            continue


if __name__ == '__main__':
    # TEST
    _test_case()
