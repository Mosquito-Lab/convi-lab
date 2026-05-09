import re
from datetime import datetime


from convi_lab.conversion_kernel.constants import TIME_PATTERNS


# Returns a match object for unit tests
def match_pattern(pattern_name: str, case: str) -> re.Match:
    """
    Return a match object for *case* against the named pattern.
    Used in unit tests and standalone ``__main__`` blocks.

    Args:
        pattern_name: Key into ``TIME_PATTERNS`` (e.g. ``"datetime"``).
        case: Raw date/time string (spaces already removed).
    Returns:
    ``re.Match`` if the pattern matches, else ``None``.
    Raises:
        KeyError:
            If *pattern_name* is not in ``TIME_PATTERNS``.
    """

    return TIME_PATTERNS[pattern_name].match(case)


# Test the output of a regex
def _test_pattern(pattern: re.Pattern, case: str) -> tuple[str, ...]:
    """
    Assert that *case* matches *pattern* and return the captured groups.

    Args:
        pattern: A compiled regex pattern.
        case: Input string to test.
    Returns:
        Tuple of captured groups.
    Raises:
        ValueError:
            If *case* does not match.
    """

    if match := pattern.match(case):
        return match.groups()

    raise ValueError(f"{case} is not a valid pattern\n Valid pattern: {pattern}")


# Remove all spaces from string
def remove_spaces(value: str) -> str:
    """Strip all whitespace characters from *value*."""

    return value.replace(' ', '')


# Used in a parser to build the datetime object
def parser_handler(date_object, time_str, am_pm):
    """
    Builds datetime object after *date_object* in a parser.

    Args:
        date_object: ``dd.mm.yyyy``
        time_str: ``HH:MM`` string
        am_pm: ``"AM"`` / ``"PM"`` / ``None``
    Returns:
        Parsed and potentially year-corrected ``datetime``.
    """

    # Good old lazy loading to avoid circling
    from convi_lab import convert_to_24_format

    time_object = convert_to_24_format(time=time_str, am_pm=am_pm)

    # Combine date and time
    _datetime = datetime.combine(date_object.date(), time_object.time())

    # Handle year boundary (if parsed date is in the past, assume next year)
    # Compare only the date part, not the time
    if date_object.date() < datetime.now().date():
        _datetime = _datetime.replace(year=datetime.now().year + 1)

    return _datetime
