"""
convert_datetime.py: the top-level entry point. It turns a raw date string into a "YYYY-MM-DD HH:MM:SS" string.
"""

from convi_lab.kernel.constants import TIME_PATTERNS
from convi_lab.parsers.process_patterns import process_patterns
from convi_lab.kernel.errors import ConviError, InvalidInputError, PatternMatchError
from convi_lab.kernel.logging_config import build_logger

logger = build_logger(__name__)


def convert_date_time(event_date: str) -> str:
    """
    Convert a raw date/time string to a normalized ``"YYYY-MM-DD HH:MM:SS"`` string.

    Whitespace between the parts is optional and can be any kind (spaces,
    tabs, non-breaking spaces), so spaced and compact variants are both
    accepted. Day and month names match in any case. The supported formats
    and the date rules are listed in the API Reference
    (docs/API_Reference.md).

    Note: this is the safe boundary. It never raises, whatever it's given
    (``None``, a number, ``pandas.NA``). Every failure is logged once and
    returns ``""``.

    Args:
        event_date: Raw date/time string (may contain spaces).
    Returns:
        ``"YYYY-MM-DD HH:MM:SS"`` on success, or ``""`` on any failure.
    Example::
        convert_date_time("17 Jul - 02:00 PM")   # "2026-07-17 14:00:00" (when run before July 17, 2026)
        convert_date_time("27/1019:30")          # "2026-10-27 19:30:00" (when run before October 27, 2026)
    """

    # The type first: a value like pandas.NA raises if its truth is tested
    if not isinstance(event_date, str) or not event_date.strip():
        logger.warning("%s", InvalidInputError(event_date))
        return ""

    # The patterns allow whitespace between parts, so only the ends are trimmed
    cleaned = event_date.strip()

    try:
        resolved = process_patterns(cleaned)

        if resolved is not None:
            return resolved.strftime("%Y-%m-%d %H:%M:%S")

        logger.warning("%s", PatternMatchError(cleaned, list(TIME_PATTERNS)))
        return ""

    except ConviError as e:
        logger.error("Parse/conversion error for '%s': %s", cleaned, e)
        return ""

    except Exception as e:
        logger.error("Unexpected error parsing '%s': %s", cleaned, e, exc_info=True)
        return ""
