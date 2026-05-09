"""
convert_clock_format.py — Normalise any HH:MM[AM|PM] string to a 24-hour datetime.
"""

from logger_lab import lab
from typing import Optional
from datetime import datetime

from convi_lab.conversion_kernel.errors import ClockFormatError

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)

# RUN CONVERT FORMAT

# Convert 12-hour to 24-hour format
def convert_to_24_format(time: str, am_pm: Optional[str] = None) -> datetime:
    """
    Parse a time string into a ``datetime`` object, normalising to 24-hour time.

    When *am_pm* is provided the input is treated as 12-hour clock; otherwise
    it is assumed to already be in 24-hour format.

    Examples:
        convert_to_24_format("14:30")          # → datetime(... 14, 30)
        convert_to_24_format("02:30", "PM")    # → datetime(... 14, 30)
        convert_to_24_format("12:00", "AM")    # → datetime(... 0, 0)
    Args:
        time: Time in ``HH:MM`` format, no spaces (e.g. ``"02:30"``).
        am_pm: Optional AM/PM suffix — case-insensitive
            (``"AM"``, ``"pm"``, ``"Pm"`` …).  Pass ``None`` for 24-hour input.
    Returns:
        ``datetime`` object carrying only the parsed time component.
    Raises:
        ClockFormatError:
            If the string cannot be parsed under the chosen format.
    """

    if am_pm:
        # 12-hour format conversion
        am_pm = am_pm.upper()
        try:
            return datetime.strptime(f"{time}{am_pm}", "%I:%M%p")

        except ValueError:
            logger.error(f"Failed to parse 12-hour time: {time}{am_pm}")
            raise ClockFormatError(time, am_pm)

    else:
        # 24-hour format
        try:
            return datetime.strptime(time, "%H:%M")

        except ValueError:
            logger.error(f"Failed to parse 24-hour time: {time}")
            raise ClockFormatError(time, None)


# Example usage and test case
def test_case():
    logger.debug(convert_to_24_format('12:36', 'AM'))


if __name__ == '__main__':
    # TEST
    test_case()