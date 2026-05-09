"""
convi-lab — Data conversion and normalization utilities.

Public API
----------
Conversions:
    convert_to_24_format  – Normalize any time string to 24-hour datetime
    convert_name          – Fuzzy-match a name against a reference list
    convert_date_time     – Master entry point: raw string → "YYYY-MM-DD HH:MM:SS"

Parsers (lower-level, used internally by convert_date_time):
    parse_day_month_time  – "17Jul-02:00PM" style strings
    parse_day_time        – "Tuesday12:30", "Today14:30" style strings
    parse_date_time       – "12/04/2522:15", "12.04.202512:15pm" style strings

Errors:
    LabError              – base; catch this for any convi-lab exception
    ParserError           – base for all parse-time failures
    ConversionError       – base for all conversion-time failures
    PatternMatchError, DayResolutionError, MonthResolutionError, DateComponentError
    ClockFormatError, FuzzyMatchError, InvalidInputError

Constants / helpers:
    DAYS, MONTHS, RELATIVE_DAYS, WEEKDAY_MAP, TIME_PATTERNS, TEST_CASES
    process_patterns
"""

from convi_lab.conversions import convert_to_24_format, convert_name, convert_date_time
from convi_lab.parsers import parse_day_month_time, parse_day_time, parse_date_time
from convi_lab.conversion_kernel.errors import (
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
)
from convi_lab.conversion_kernel.constants import DAYS, MONTHS, RELATIVE_DAYS, WEEKDAY_MAP, TIME_PATTERNS, TEST_CASES
from convi_lab.conversion_kernel.pattern_parsers import process_patterns

__all__ = [
    # Conversions
    "convert_to_24_format",
    "convert_name",
    "convert_date_time",
    # Parsers
    "parse_day_month_time",
    "parse_day_time",
    "parse_date_time",
    # Errors — root
    "LabError",
    # Errors — parsers
    "ParserError",
    "PatternMatchError",
    "DayResolutionError",
    "MonthResolutionError",
    "DateComponentError",
    # Errors — conversions
    "ConversionError",
    "ClockFormatError",
    "FuzzyMatchError",
    "InvalidInputError",
    # Constants
    "DAYS",
    "MONTHS",
    "RELATIVE_DAYS",
    "WEEKDAY_MAP",
    "TIME_PATTERNS",
    "TEST_CASES",
    # Helpers
    "process_patterns",
]
