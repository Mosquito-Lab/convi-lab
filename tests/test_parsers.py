"""
``process_patterns``: routing to the right parser, and the typed errors it lets through.

Unlike ``convert_date_time``, it raises typed errors instead of returning ``""``. Spaced and
compact input both match.
"""

from datetime import datetime

import pytest

from convi_lab import (
    TIME_PATTERNS,
    ClockFormatError,
    DateComponentError,
    parse_date_time,
    parse_day_month_time,
    parse_day_time,
    process_patterns,
)
from convi_lab.parsers.process_patterns import PATTERN_HANDLERS


def test_each_pattern_is_routed_to_its_parser():
    """One compact input per pattern comes back as the right ``datetime``."""

    cases = {
        "day_time": ("Fri02:30PM", datetime(2026, 5, 15, 14, 30)),
        "day_month_time": ("17Jul-02:00PM", datetime(2026, 7, 17, 14, 0)),
        "datetime": ("17/07/2622:15", datetime(2026, 7, 17, 22, 15)),
    }
    assert set(cases) == set(TIME_PATTERNS)  # Every pattern has a case

    for pattern_name, (raw, expected) in cases.items():
        assert TIME_PATTERNS[pattern_name].match(raw), pattern_name
        assert process_patterns(raw) == expected, pattern_name


def test_every_pattern_has_exactly_one_parser():
    """The pattern table and the parser table share their names (PS-5)."""

    assert PATTERN_HANDLERS.keys() == TIME_PATTERNS.keys()


def test_parsers_take_an_explicit_today():
    """Each parser resolves its date against ``today=`` when it's given, instead of the clock."""

    new_years_eve = datetime(2026, 12, 31, 23, 0)
    cases = [
        (parse_date_time, "datetime", "05/0110:00", datetime(2027, 1, 5, 10, 0)),
        (parse_day_month_time, "day_month_time", "05Jan10:00", datetime(2027, 1, 5, 10, 0)),
        (parse_day_time, "day_time", "Today10:00", datetime(2026, 12, 31, 10, 0)),
        (parse_day_time, "day_time", "Fri10:00", datetime(2027, 1, 1, 10, 0)),
    ]
    for parser, pattern_name, raw, expected in cases:
        match = TIME_PATTERNS[pattern_name].match(raw)
        assert match, raw
        assert parser(match, today=new_years_eve) == expected, raw


def test_no_match_returns_none():
    """Input that matches no pattern returns ``None``."""

    assert process_patterns("garbage") is None


def test_typed_errors_reach_the_caller():
    """A matched input with an impossible part raises the parser's typed error."""

    cases = {
        "31/0210:00": DateComponentError,  # datetime pattern
        "31Feb10:00": DateComponentError,  # day_month_time pattern
        "Today13:00PM": ClockFormatError,  # day_time pattern
    }
    for raw, error in cases.items():
        with pytest.raises(error):
            process_patterns(raw)
