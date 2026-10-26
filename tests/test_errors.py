"""
The error hierarchy and the message each error builds.
"""

from convi_lab import (
    ClockFormatError,
    ConversionError,
    ConviError,
    DateComponentError,
    DayResolutionError,
    FuzzyMatchError,
    InvalidInputError,
    InvalidReferenceError,
    LabError,
    MonthResolutionError,
    ParserError,
    PatternMatchError,
)


def test_hierarchy():
    """Every error is a ``ConviError``, under the parser or the conversion branch.

    ``LabError`` is its old name (KN-10).
    """

    assert LabError is ConviError

    branches = {
        ParserError: [PatternMatchError, DayResolutionError, MonthResolutionError, DateComponentError],
        ConversionError: [ClockFormatError, FuzzyMatchError, InvalidInputError, InvalidReferenceError],
    }
    for branch, errors in branches.items():
        assert issubclass(branch, ConviError)
        for error in errors:
            assert issubclass(error, branch), error


def test_messages():
    """Each error names the bad value, and the valid ones where there is a list."""

    cases = [
        (
            PatternMatchError("badstring", ["day_time", "datetime"]),
            "'badstring' did not match any known pattern. Available patterns: day_time, datetime",
        ),
        (
            DayResolutionError("Xyz"),
            "'Xyz' could not be resolved to a weekday or relative day. "
            "Valid values: Today, Tomorrow, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday",
        ),
        (
            MonthResolutionError("Jly"),
            "'Jly' could not be resolved to a calendar month. "
            "Valid values: January, February, March, April, May, June, "
            "July, August, September, October, November, December",
        ),
        (
            DateComponentError("/999", "year fragment must be 2 or 4 digits"),
            "date fragment '/999' is malformed: year fragment must be 2 or 4 digits",
        ),
        (FuzzyMatchError("xyz", 1), "fuzzy match found no result for 'xyz' in a reference list of 1 item"),
        (FuzzyMatchError("xyz", 12), "fuzzy match found no result for 'xyz' in a reference list of 12 items"),
        (InvalidInputError(None), "expected a non-empty str, got NoneType: None"),
        (InvalidInputError(""), "expected a non-empty str, got an empty string"),
        (InvalidInputError("   "), "expected a non-empty str, got a blank string"),
        (InvalidReferenceError(None), "expected an iterable of names, got NoneType: None"),
    ]
    for error, message in cases:
        assert str(error) == message
