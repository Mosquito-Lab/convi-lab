"""
errors.py: the exception hierarchy for convi-lab.

All exceptions inherit from ``ConviError``, so library consumers can
write a single broad ``except ConviError`` or catch specific subclasses
for fine-grained handling.

Hierarchy
---------
::

    ConviError (LabError is its old name)
    ├── ParserError
    │   ├── PatternMatchError      no TIME_PATTERNS entry matched the raw input
    │   ├── DayResolutionError     weekday or relative-day string is unresolvable
    │   ├── MonthResolutionError   month name string is unresolvable
    │   └── DateComponentError     the day, month and year don't make a real date
    └── ConversionError
        ├── ClockFormatError       HH:MM[AM|PM] string failed to parse
        ├── FuzzyMatchError        no match: empty reference, below score_cutoff, or rapidfuzz raised
        ├── InvalidInputError      bad type or empty string passed to convert_date_time
        └── InvalidReferenceError  convert_name's reference isn't a collection of names

``PatternMatchError``, ``DayResolutionError`` and ``MonthResolutionError`` are
reserved: nothing raises them in 0.1.x.

Design notes
------------
* Every leaf class accepts the minimum arguments needed to produce a
  self-describing message, so callers never have to format strings
  themselves.
* ``errors.py`` imports only ``kernel.constants``. It sits at the base of
  the dependency graph and is safe to import from anywhere.
* ``convert_date_time`` is the only public function that swallows
  ``ConviError``. All other callables let errors propagate so the caller
  can decide how to handle them.
"""

from convi_lab.kernel.constants import DAYS, MONTHS

########
# Root #
########


class ConviError(Exception):
    """
    Base class for all convi-lab exceptions.

    Catch this to handle any error the library can raise. It was called
    ``LabError`` before 0.1.1, a name logger-lab also uses for its own base.

    Example::
        try:
            result = process_patterns(raw)
        except ConviError as exc:
            print(f'convi-lab error: {exc}')
    """


LabError = ConviError  # The old name, kept so existing `except LabError` clauses still work (KN-10)


#################
# Parser errors #
#################


class ParserError(ConviError):
    """
    Base class for all parse-time failures.

    Raised (or subclassed) whenever a raw string cannot be turned into a
    ``datetime``. Either no regex pattern matched, or a matched component
    (day, month, date fragment) could not be resolved to a concrete value.
    """


class PatternMatchError(ParserError):
    """
    Describes an input that no entry in ``TIME_PATTERNS`` matches.

    Note: reserved. ``process_patterns()`` returns ``None`` instead of
    raising it, and ``convert_date_time()`` logs its message.

    Args:
        input_str: The input that was tested, trimmed at both ends.
        available_patterns: The pattern names that were tried.
    Example::
        raise PatternMatchError("badstring", ["day_time", "day_month_time", "datetime"])
        # PatternMatchError: 'badstring' did not match any known pattern.
        # Available patterns: day_time, day_month_time, datetime
    """

    def __init__(self, input_str: str, available_patterns: list[str]) -> None:
        patterns = ", ".join(available_patterns)

        super().__init__(
            f"'{input_str}' did not match any known pattern. "
            f"Available patterns: {patterns}"
        )


class DayResolutionError(ParserError):
    """
    Describes a day string that can't be resolved to a weekday or relative day.

    Note: reserved. The ``day_time`` pattern only admits real day spellings,
    so ``parse_day_time()`` always resolves its day.

    Args:
        day_str: The raw day string that could not be resolved
            (e.g. ``"Mnday"``, ``"Xyz"``).
    Example::
        raise DayResolutionError("Xyz")
        # DayResolutionError: 'Xyz' could not be resolved to a weekday or
        # relative day. Valid values: Today, Tomorrow, Monday … Sunday
    """

    def __init__(self, day_str: str) -> None:
        valid = ", ".join(DAYS)

        super().__init__(
            f"'{day_str}' could not be resolved to a weekday or relative day. "
            f"Valid values: {valid}"
        )


class MonthResolutionError(ParserError):
    """
    Describes a month string that can't be resolved to a calendar month.

    Note: reserved. The ``day_month_time`` pattern only admits real month
    spellings, so ``parse_day_month_time()`` always resolves its month.

    Args:
        month_str: The raw month string that could not be resolved
            (e.g. ``"Jly"``, ``"Xyz"``).
    Example::
        raise MonthResolutionError("Jly")
        # MonthResolutionError: 'Jly' could not be resolved to a calendar month.
        # Valid values: January, February, … December
    """

    def __init__(self, month_str: str) -> None:
        valid = ", ".join(MONTHS)

        super().__init__(
            f"'{month_str}' could not be resolved to a calendar month. "
            f"Valid values: {valid}"
        )


class DateComponentError(ParserError):
    """
    Raised when a day, month and year don't make a real date.

    Fired by ``resolve_date()`` when no year makes the day and month real
    (``31/04``), or the given year doesn't (``29/02/2027``). The patterns
    already keep days within 1 to 31 and months within 1 to 12.

    Args:
        fragment: The date that could not be made, as ``dd.mm`` or
            ``dd.mm.yyyy`` (e.g. ``"31.04"``, ``"29.02.2027"``).
        reason: Human-readable explanation of what went wrong.
    Example::
        raise DateComponentError("31.04", "day is out of range for month")
        # DateComponentError: date fragment '31.04' is malformed:
        #   day is out of range for month
    """

    def __init__(self, fragment: str, reason: str) -> None:
        super().__init__(
            f"date fragment '{fragment}' is malformed: {reason}"
        )


#####################
# Conversion errors #
#####################


class ConversionError(ConviError):
    """
    Base class for all conversion-time failures.

    Raised (or subclassed) whenever a structurally valid component
    (time string, fuzzy name query, or entry-point input) cannot be
    converted to its target type.
    """


class ClockFormatError(ConversionError):
    """
    Raised when an HH:MM[AM|PM] string cannot be parsed.

    Fired by ``convert_to_24_format()`` when the time isn't ``HH:MM``, the
    suffix isn't AM or PM, or a 12-hour time's hour isn't 1 to 12.

    Args:
        time: The raw ``HH:MM`` fragment (e.g. ``"25:00"``, ``"9:99"``).
        am_pm: The AM/PM suffix if 12-hour mode was requested, else ``None``.
    Example::
        raise ClockFormatError("25:00", None)
        # ClockFormatError: cannot parse '25:00' as a 24-hour time (HH:MM)

        raise ClockFormatError("09:99", "PM")
        # ClockFormatError: cannot parse '09:99PM' as a 12-hour time (HH:MM AM/PM)
    """

    def __init__(self, time: str, am_pm: str | None) -> None:
        if am_pm:
            raw = f"{time}{am_pm.upper()}"
            fmt = "12-hour time (HH:MM AM/PM)"
        else:
            raw = time
            fmt = "24-hour time (HH:MM)"

        super().__init__(f"cannot parse '{raw}' as a {fmt}")


class FuzzyMatchError(ConversionError):
    """
    Raised when ``convert_name()`` finds no match for the given query.

    Fired when the reference is empty, when nothing reaches the caller's
    ``score_cutoff``, or when rapidfuzz raises.

    Args:
        name: The query string that could not be matched.
        ref_count: Number of items in the reference list (aids debugging).
    Example::
        raise FuzzyMatchError("xyz", 12)
        # FuzzyMatchError: fuzzy match found no result for 'xyz'
        #   in a reference list of 12 items
    """

    def __init__(self, name: str, ref_count: int) -> None:
        super().__init__(
            f"fuzzy match found no result for '{name}' "
            f"in a reference list of {ref_count} item{'s' if ref_count != 1 else ''}"
        )


class InvalidInputError(ConversionError):
    """
    Describes a value passed to ``convert_date_time()`` that is not a
    non-empty string.

    Note: ``convert_date_time()`` never raises it. It logs the message and
    returns ``""``. Any value works, ``pandas.NA`` included.

    Args:
        value: The invalid value that was provided.
    Example::
        str(InvalidInputError(None))
        # "expected a non-empty str, got NoneType: None"

        str(InvalidInputError(""))
        # "expected a non-empty str, got an empty string"

        str(InvalidInputError("   "))
        # "expected a non-empty str, got a blank string"
    """

    def __init__(self, value: object) -> None:
        # The type first: a value like pandas.NA raises if compared and tested
        if isinstance(value, str) and not value.strip():
            detail = "got an empty string" if value == "" else "got a blank string"

        else:
            detail = f"got {type(value).__name__}: {value!r}"

        super().__init__(f"expected a non-empty str, {detail}")


class InvalidReferenceError(ConversionError):
    """
    Raised when ``convert_name()`` gets a reference that isn't a collection of names.

    That is a value it can't iterate (``None``), or a single string, which
    would be matched letter by letter.

    Args:
        value: The reference that was provided.
    Example::
        raise InvalidReferenceError(None)
        # InvalidReferenceError: expected an iterable of names, got NoneType: None
    """

    def __init__(self, value: object) -> None:
        super().__init__(f"expected an iterable of names, got {type(value).__name__}: {value!r}")
