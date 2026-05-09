"""
convert_datetime.py — Top-level entry point: raw date string → ISO-style string.
"""

from logger_lab import lab

from convi_lab.conversion_kernel.utils import remove_spaces
from convi_lab.conversion_kernel.constants import TEST_CASES
from convi_lab.conversion_kernel.constants import TIME_PATTERNS
from convi_lab.conversion_kernel.pattern_parsers import process_patterns
from convi_lab.conversion_kernel.errors import LabError, InvalidInputError

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)


# Convert a string of time into standard datetime
def convert_date_time(event_date: str) -> str:
    """
    Convert a raw date/time string to a normalised ``"YYYY-MM-DD HH:MM:SS"`` string.

    Spaces are stripped automatically before matching, so both spaced and
    compact variants are accepted.

    Supported input formats (``[AM|PM]`` is always optional):
    ========================================= ================================
    Format                                    Example
    ========================================= ================================
    ``dd/mm HH:MM [AM|PM]``                   ``"12/04 22:15"``,
    ``dd/mm/yy HH:MM [AM|PM]``                ``"12/04/25 22:15 PM"``
    ``dd.mm.yyyy HH:MM [AM|PM]``              ``"12.04.2025 12:15 pm"``
    ``Day HH:MM [AM|PM]``                     ``"Tuesday 12:30"``,
    ``Today/Tomorrow HH:MM [AM|PM]``          ``"Today 14:30"``
    ``ddMon-HH:MM [AM|PM]``                   ``"17 Jul - 02:00 PM"``
    ========================================= ================================

    Args:
        event_date: Raw date/time string (may contain spaces).
    Returns:
        ``"YYYY-MM-DD HH:MM:SS"`` on success, or ``""`` on any failure.
    """

    if not event_date or not isinstance(event_date, str):
        logger.warning(str(InvalidInputError(event_date)))
        return ''

    # Remove all spaces from input
    _event_date = remove_spaces(event_date.strip())
    if not _event_date:
        logger.warning(str(InvalidInputError("")))
        return ""

    try:
        _datetime = process_patterns(_event_date)

        if _datetime:
            return _datetime.strftime("%Y-%m-%d %H:%M:%S")

        logger.warning(
            f"No pattern matched '{_event_date}'. "
            f"Available patterns: {list(TIME_PATTERNS.keys())}"
        )
        return ''


    except LabError as e:
        logger.error(f"Parse/conversion error for '{_event_date}': {e}")
        return ""

    except Exception as e:
        logger.error(f"Unexpected error parsing '{_event_date}': {e}", exc_info=True)
        return ""


# Example usage and test cases
def test_case():
    """ Test multiple cases for event_date """

    print("Testing space removal and AM/PM support:")
    print("=" * 80)
    for test in TEST_CASES:
        result = convert_date_time(test)
        logger.debug(f"{test} -> {result}")


if __name__ == "__main__":
    # TEST
    test_case()
