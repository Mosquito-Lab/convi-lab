"""
errors.py — Exception hierarchy for convi-lab.

All exceptions inherit from :class:`LabError` so library consumers can
write a single broad ``except LabError`` or catch specific subclasses
for fine-grained handling.

Hierarchy
---------
::

    LabError
    ├── ParserError
    │   ├── PatternMatchError      no TIME_PATTERNS entry matched the raw input
    │   ├── DayResolutionError     weekday or relative-day string is unresolvable
    │   ├── MonthResolutionError   month name string is unresolvable
    │   └── DateComponentError     numeric date fragment (day/month/year) is malformed
    └── ConversionError
        ├── ClockFormatError       HH:MM[AM|PM] string failed to parse
        ├── FuzzyMatchError        rapidfuzz returned no result or raised internally
        └── InvalidInputError      bad type or empty string passed to convert_date_time

Design notes
------------
* Every leaf class accepts the minimum arguments needed to produce a
  self-describing message so callers never have to format strings
  themselves.
* ``errors.py`` imports nothing from the rest of the package — it sits
  at the base of the dependency graph and is safe to import from anywhere.
* ``convert_date_time`` is the only public function that swallows
  ``LabError``; all other callables let errors propagate so the caller
  can decide how to handle them.
"""

########
# Root #
########

class LabError(Exception):
    """
    Base class for all convi-lab exceptions.

    Catch this to handle any error the library can raise::

        try:
            result = convert_date_time(raw)
        except LabError as exc:
            print(f' convi-lab error: {exc}')
    """

##################
# Parser errors  #
##################

class ParserError(LabError):
    """
    Base class for all parse-time failures.

    Raised (or subclassed) whenever a raw string cannot be turned into a
    ``datetime`` — either because no regex pattern matched or because a
    matched component (day, month, date fragment) could not be resolved
    to a concrete value.
    """

class PatternMatchError(ParserError):
    """
    Raised when no entry in ``TIME_PATTERNS`` matches the input string.
    This fires in `process_patterns()` after all patterns have been tried
     and none produced a match.

    Example:
        raise PatternMatchError("badstring", ["day_time", "day_month_time", "datetime"])
        # PatternMatchError: 'badstring' did not match any known pattern.
        # Available patterns: day_time, day_month_time, datetime
    Args:
        input_str: The cleaned (space-stripped) string that was tested.
        available_patterns: Sequence of pattern names that were tried.
    """

    def __init__(self, input_str: str, available_patterns: list[str]) -> None:
        patterns = ", ".join(available_patterns)

        super().__init__(
            f"'{input_str}' did not match any known pattern. "
            f"Available patterns: {patterns}"
        )

class DayResolutionError(ParserError):
    """
    Raised when a day string cannot be resolved to a weekday or relative day.

    Fired inside `parse_day_time()` when fuzzy matching returns a value that
    is neither in ``WEEKDAY_MAP`` nor in ``RELATIVE_DAYS``.

    Example:
        raise DayResolutionError("Xyz")
        # DayResolutionError: 'Xyz' could not be resolved to a weekday or
        # relative day. Valid values: Today, Tomorrow, Monday … Sunday
    Args:
        day_str: The raw day string that could not be resolved
                 (e.g. ``"Mnday"``, ``"Xyz"``).
    """

    _VALID = (
        "Today", "Tomorrow",
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    )

    def __init__(self, day_str: str) -> None:
        valid = ", ".join(self._VALID)

        super().__init__(
            f"'{day_str}' could not be resolved to a weekday or relative day. "
            f"Valid values: {valid}"
        )

class MonthResolutionError(ParserError):
    """
    Raised when a month string cannot be resolved to a calendar month.

    Fired inside `parse_day_month_time()` when fuzzy matching returns
    an empty result for the month component.

    Example:
        raise MonthResolutionError("Jly")
        # MonthResolutionError: 'Jly' could not be resolved to a calendar month.
        # Valid values: January, February, … December
    Args:
        month_str: The raw month string that could not be resolved
                   (e.g. ``"Jly"``, ``"Xyz"``).
    """

    _VALID = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    )

    def __init__(self, month_str: str) -> None:
        valid = ", ".join(self._VALID)

        super().__init__(
            f"'{month_str}' could not be resolved to a calendar month. "
            f"Valid values: {valid}"
        )

class DateComponentError(ParserError):
    """
    Raised when a numeric date fragment is structurally malformed.

    Covers year fragments (``"/99"``, ``".20255"``), day-of-month values
    outside 1–31, and month numbers outside 1–12 that pass regex
    screening but fail ``datetime.strptime``.

    Example:
        raise DateComponentError("/999", "year fragment must be 2 or 4 digits")
        # DateComponentError: date fragment '/999' is malformed:
        #   year fragment must be 2 or 4 digits
    Args:
        fragment: The raw string fragment that could not be parsed
                  (e.g. ``"/999"``, ``"32/13"``).
        reason:   Human-readable explanation of what went wrong.
    """

    def __init__(self, fragment: str, reason: str) -> None:
        super().__init__(
            f"date fragment '{fragment}' is malformed: {reason}"
        )


######################
# Conversion errors  #
######################

class ConversionError(LabError):
    """
    Base class for all conversion-time failures.

    Raised (or subclassed) whenever a structurally valid component
    (time string, fuzzy name query, or entry-point input) cannot be
    converted to its target type.
    """

class ClockFormatError(ConversionError):
    """
    Raised when an HH:MM[AM|PM] string cannot be parsed.

    Fired by `convert_to_24_format()` when `datetime.strptime()`
    rejects the assembled time string.

     Example:
        raise ClockFormatError("25:00", None)
        # ClockFormatError: cannot parse '25:00' as a 24-hour time (HH:MM)

        raise ClockFormatError("09:99", "PM")
        # ClockFormatError: cannot parse '09:99PM' as a 12-hour time (HH:MM AM/PM)
    Args:
        time:   The raw ``HH:MM`` fragment (e.g. ``"25:00"``, ``"9:99"``).
        am_pm:  The AM/PM suffix if 12-hour mode was requested, else ``None``.
    """

    def __init__(self, time: str, am_pm: str | None) -> None:
        if am_pm:
            raw  = f"{time}{am_pm.upper()}"
            fmt  = "12-hour time (HH:MM AM/PM)"
        else:
            raw  = time
            fmt  = "24-hour time (HH:MM)"

        super().__init__(f"cannot parse '{raw}' as a {fmt}")

class FuzzyMatchError(ConversionError):
    """
    Raised when rapidfuzz finds no match for the given query.

    Fired by `convert_name()` when ``process.extractOne``
    returns ``None`` or raises internally.

    Example:
        raise FuzzyMatchError("xyz", 12)
        # FuzzyMatchError: fuzzy match found no result for 'xyz'
        #   in a reference list of 12 items
    Args:
        name:      The query string that could not be matched.
        ref_count: Number of items in the reference list (aids debugging).
    """

    def __init__(self, name: str, ref_count: int) -> None:
        super().__init__(
            f"fuzzy match found no result for '{name}' "
            f"in a reference list of {ref_count} item{'s' if ref_count != 1 else ''}"
        )

class InvalidInputError(ConversionError):
    """
    Raised when the value passed to ``convert_date_time()`` is not a
    non-empty string.

    Example:
        raise InvalidInputError(None)
        # InvalidInputError: expected a non-empty str, got NoneType: None

        raise InvalidInputError("")
        # InvalidInputError: expected a non-empty str, got an empty string
    Args:
        value: The invalid value that was provided.
    """

    def __init__(self, value: object) -> None:
        if value == "":
            detail = "got an empty string"

        else:
            detail = f"got {type(value).__name__}: {value!r}"

        super().__init__(f"expected a non-empty str, {detail}")
