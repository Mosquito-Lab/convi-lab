"""
convi-lab: data conversion and normalization utilities.

The public names are listed once, in ``__all__`` below, grouped by kind. The
API Reference (docs/API_Reference.md) describes each one.

``__version__`` is the installed version, read from the package metadata.
"""

import importlib.metadata

from convi_lab.conversions import convert_to_24_format, convert_name, convert_date_time
from convi_lab.parsers import parse_day_month_time, parse_day_time, parse_date_time
from convi_lab.kernel.errors import (
    ConviError,
    LabError,
    ParserError,
    PatternMatchError,
    DayResolutionError,
    MonthResolutionError,
    DateComponentError,
    ConversionError,
    ClockFormatError,
    FuzzyMatchError,
    InvalidInputError,
    InvalidReferenceError,
)
from convi_lab.kernel.constants import DAYS, MONTHS, RELATIVE_DAYS, WEEKDAY_MAP, TIME_PATTERNS
from convi_lab.parsers.process_patterns import process_patterns

__version__ = importlib.metadata.version("convi-lab")  # pyproject.toml is the one place the version is written

__all__ = [
    # Conversions
    "convert_to_24_format",
    "convert_name",
    "convert_date_time",
    # Parsers
    "parse_day_month_time",
    "parse_day_time",
    "parse_date_time",
    # Errors: root
    "ConviError",
    "LabError",
    # Errors: parsers
    "ParserError",
    "PatternMatchError",
    "DayResolutionError",
    "MonthResolutionError",
    "DateComponentError",
    # Errors: conversions
    "ConversionError",
    "ClockFormatError",
    "FuzzyMatchError",
    "InvalidInputError",
    "InvalidReferenceError",
    # Constants
    "DAYS",
    "MONTHS",
    "RELATIVE_DAYS",
    "WEEKDAY_MAP",
    "TIME_PATTERNS",
    # Helpers
    "process_patterns",
]
