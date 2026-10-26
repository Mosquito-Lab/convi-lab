"""
convert_clock_format.py: read an HH:MM[AM|PM] string as a 24-hour time.
"""

from datetime import datetime

from convi_lab.kernel.errors import ClockFormatError


def convert_to_24_format(time: str, am_pm: str | None = None) -> datetime:
    """
    Parse a time string into a ``datetime`` object, normalizing to 24-hour time.

    When *am_pm* is provided the input is treated as 12-hour clock. Otherwise
    it is assumed to already be in 24-hour format. The 12-hour clock is
    converted with arithmetic, never with the locale's AM/PM names, so the
    result is the same in every locale.

    Args:
        time: Time in ``HH:MM`` format, no spaces (e.g. ``"02:30"``).
        am_pm: Optional AM/PM suffix, case-insensitive
            (``"AM"``, ``"pm"``, ``"Pm"`` …). Pass ``None`` for 24-hour input.
    Returns:
        ``datetime`` object carrying only the parsed time component.
    Raises:
        `ClockFormatError`: when the string cannot be parsed under the chosen format.
    Example::
        convert_to_24_format(time="14:30")               # datetime(1900, 1, 1, 14, 30)
        convert_to_24_format(time="02:30", am_pm="PM")   # datetime(1900, 1, 1, 14, 30)
        convert_to_24_format(time="12:00", am_pm="AM")   # datetime(1900, 1, 1, 0, 0)
    """

    # %H and %M are digits only, so this read never depends on the locale
    try:
        parsed = datetime.strptime(time, "%H:%M")

    except ValueError as err:
        raise ClockFormatError(time=time, am_pm=am_pm) from err

    if not am_pm:
        return parsed

    # 12-hour clock: hours 1 to 12, then AM keeps them (12 becomes 0) and PM adds 12
    suffix = am_pm.upper()
    if suffix not in ("AM", "PM") or not 1 <= parsed.hour <= 12:
        raise ClockFormatError(time=time, am_pm=am_pm)

    return parsed.replace(hour=parsed.hour % 12 + (12 if suffix == "PM" else 0))
