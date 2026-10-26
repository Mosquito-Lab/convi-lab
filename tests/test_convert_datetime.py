"""
``convert_date_time``: every supported format, the date rules, and the safe ``""`` boundary.

The clock is frozen at Wednesday 2026-05-13 10:00 (``conftest.NOW``).
"""

from datetime import datetime

from convi_lab import convert_date_time, process_patterns

SAMPLES = [  # The sample inputs the package used to export as TEST_CASES (KN-3)
    "12/04 22:15",
    "12/04 10:15 PM",
    "Tuesday 12:30",
    "Tuesday 12:30 PM",
    "12.04.2025 12:15",
    "12.04.2025 12:15 pm",
    "Tuesday 02:30 PM",
    "17 Jul - 02:00",
    "17 Jul - 02:00 PM",
    "Today 14:30",
    "Tomorrow 03:30 PM",
    "12/0422:15",
    "Tuesday12:30PM",
    "17Jul-02:00PM",
    "Wed1:30am",
]

FORMATS = {  # Raw input -> normalized output, one or more per supported format
    "17/07 22:15": "2026-07-17 22:15:00",  # dd/mm
    "17/07 10:15 PM": "2026-07-17 22:15:00",
    "17/07/26 22:15": "2026-07-17 22:15:00",  # dd/mm/yy
    "17.07.2026 12:15 pm": "2026-07-17 12:15:00",  # dd.mm.yyyy, lowercase pm
    "17.07.2027 00:30": "2027-07-17 00:30:00",  # A future year is kept
    "Friday 12:30": "2026-05-15 12:30:00",  # Day
    "Fri 02:30 PM": "2026-05-15 14:30:00",  # Abbreviated day
    "Today 14:30": "2026-05-13 14:30:00",
    "Tomorrow 03:30 PM": "2026-05-14 15:30:00",
    "17 Jul - 02:00 PM": "2026-07-17 14:00:00",  # ddMon-HH:MM
    "17 July 14:00": "2026-07-17 14:00:00",  # Full month name, no dash
}


def test_every_format_spaced_and_compact():
    """Each format gives the same result with its spaces and without them."""

    for raw, expected in FORMATS.items():
        assert convert_date_time(raw) == expected, raw
        assert convert_date_time(raw.replace(" ", "")) == expected, raw


def test_arbi_core_scraped_shape():
    """arbi-core's scraper cuts each row to ten characters: ``dd/mmHH:MM``, no spaces, no year."""

    cases = {
        "27/1019:30": "2026-10-27 19:30:00",
        "01/1100:30": "2026-11-01 00:30:00",
        "05/1209:00": "2026-12-05 09:00:00",
        "31/1223:59": "2026-12-31 23:59:00",
        "10/0118:00": "2027-01-10 18:00:00",  # January is past: next year
    }
    for raw, expected in cases.items():
        assert convert_date_time(raw) == expected, raw


def test_any_year_with_two_or_four_digits():
    """Years outside 2025 to 2029 parse too (KN-6)."""

    assert convert_date_time("17.07.2030 10:00") == "2030-07-17 10:00:00"
    assert convert_date_time("17/07/30 10:00") == "2030-07-17 10:00:00"
    assert convert_date_time("17/07/2099 10:00") == "2099-07-17 10:00:00"


def test_single_digit_day_and_month():
    """One-digit days and months parse. Kept spaces keep ambiguous inputs apart (KN-7)."""

    assert convert_date_time("7/06 10:00") == "2026-06-07 10:00:00"
    assert convert_date_time("17/6 10:00") == "2026-06-17 10:00:00"
    assert convert_date_time("7 Jul 10:00") == "2026-07-07 10:00:00"
    assert convert_date_time("1/11 1:00") == "2026-11-01 01:00:00"
    assert convert_date_time("1/1 11:00") == "2027-01-01 11:00:00"


def test_any_whitespace_between_parts():
    """Tabs and non-breaking spaces count as spaces (KN-5)."""

    assert convert_date_time("17 Jul\t10:00") == "2026-07-17 10:00:00"
    assert convert_date_time("17\u00a0Jul 10:00") == "2026-07-17 10:00:00"  # A non-breaking space
    assert convert_date_time("17 / 07  10 : 15") == "2026-07-17 10:15:00"


def test_names_in_any_case():
    """Day and month names match whatever their case (KN-11)."""

    assert convert_date_time("monday 12:30") == "2026-05-18 12:30:00"
    assert convert_date_time("MON 12:30") == "2026-05-18 12:30:00"
    assert convert_date_time("today 14:30") == "2026-05-13 14:30:00"
    assert convert_date_time("17 JUL 10:00") == "2026-07-17 10:00:00"


def test_common_abbreviations():
    """The four-letter forms people write are recognized (KN-12)."""

    assert convert_date_time("Tues 12:30") == "2026-05-19 12:30:00"
    assert convert_date_time("Weds 12:30") == "2026-05-20 12:30:00"
    assert convert_date_time("Thurs 12:30") == "2026-05-14 12:30:00"
    assert convert_date_time("Thur 12:30") == "2026-05-14 12:30:00"
    assert convert_date_time("17 Sept 10:00") == "2026-09-17 10:00:00"


def test_made_up_names_are_rejected():
    """An abbreviation with another name's ending is not a name (KN-13)."""

    for raw in ["Monurday 12:30", "Todaynesday 12:30", "17 Decuary 10:00", "17 Janember 10:00"]:
        assert convert_date_time(raw) == "", raw


def test_samples_all_convert():
    """Every sample input converts to a date."""

    for raw in SAMPLES:
        assert convert_date_time(raw), raw


def test_past_date_moves_to_next_year():
    """A date already past this year resolves to next year. Only the date counts, not the time."""

    assert convert_date_time("17/01 09:00") == "2027-01-17 09:00:00"
    assert convert_date_time("17 Jan - 09:00") == "2027-01-17 09:00:00"
    assert convert_date_time("13/05 08:00") == "2026-05-13 08:00:00"  # Today, earlier hour


def test_a_given_year_is_kept():
    """A date with a year is that exact date, even in the past (PS-1)."""

    assert convert_date_time("12.04.2025 22:15") == "2025-04-12 22:15:00"
    assert convert_date_time("12/04/26 10:00") == "2026-04-12 10:00:00"
    assert convert_date_time("17/07/2027 10:00") == "2027-07-17 10:00:00"


def test_february_29_is_the_next_real_one(clock):
    """Without a year, Feb 29 is the next leap year's. It never raises a bare ValueError (PS-2)."""

    assert convert_date_time("29/02 10:00") == "2028-02-29 10:00:00"
    assert convert_date_time("29 Feb 10:00") == "2028-02-29 10:00:00"

    clock(datetime(2028, 3, 1, 10, 0))  # Just after a Feb 29
    assert convert_date_time("29/02 10:00") == "2032-02-29 10:00:00"
    assert process_patterns("29/02 10:00") == datetime(2032, 2, 29, 10, 0)

    assert convert_date_time("29/02/2027 10:00") == ""  # A given year with no Feb 29


def test_the_clock_is_read_once_per_conversion(clock):
    """A conversion that runs across midnight on New Year's Eve uses one "today" (PS-9)."""

    new_year = (datetime(2026, 12, 31, 23, 59, 59), datetime(2027, 1, 1, 0, 0, 0))

    clock(*new_year)
    assert convert_date_time("05/01 10:00") == "2027-01-05 10:00:00"
    clock(*new_year)
    assert convert_date_time("Today 10:00") == "2026-12-31 10:00:00"
    clock(*new_year)
    assert convert_date_time("05 Jan 10:00") == "2027-01-05 10:00:00"


def test_weekday_is_always_the_next_one():
    """Today's own weekday name means a week from today, never today."""

    assert convert_date_time("Wednesday 12:00") == "2026-05-20 12:00:00"
    assert convert_date_time("Tuesday 12:00") == "2026-05-19 12:00:00"


def test_bad_input_returns_empty_string():
    """Bad types, blanks, unmatched text and unparseable parts all return ``""``."""

    bad_inputs = [
        None,
        42,
        "",
        "   ",
        "garbage",
        "31/02 10:00",  # No February 31st (DateComponentError inside)
        "Today 13:00 PM",  # No 13 o'clock on a 12-hour clock (ClockFormatError inside)
    ]
    for value in bad_inputs:
        assert convert_date_time(value) == "", value  # pyrefly: ignore  # Deliberate wrong types


class Missing:
    """A value whose truth can't be tested, like ``pandas.NA``: ``bool()`` and ``==`` both refuse."""

    def __bool__(self) -> bool:
        """Refuse, like ``pandas.NA``."""

        raise TypeError("boolean value of NA is ambiguous")

    def __eq__(self, other: object) -> bool:
        """Refuse, like testing the result of ``pandas.NA == ...``."""

        raise TypeError("boolean value of NA is ambiguous")


def test_missing_values_return_empty_string():
    """A value like ``pandas.NA`` returns ``""``, never raises (CV-10)."""

    assert convert_date_time(Missing()) == ""  # pyrefly: ignore  # Deliberate wrong type
