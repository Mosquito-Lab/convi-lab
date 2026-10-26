"""
The two building-block conversions: ``convert_to_24_format`` and ``convert_name``.
"""

import locale

import pytest

from convi_lab import (
    DAYS,
    MONTHS,
    ClockFormatError,
    FuzzyMatchError,
    InvalidReferenceError,
    convert_date_time,
    convert_name,
    convert_to_24_format,
)

GERMAN_LOCALES = ["German_Germany.1252", "de_DE.UTF-8", "de_DE"]  # Windows name first, then POSIX


@pytest.fixture
def german_time_locale():
    """Switch ``LC_TIME`` to German for one test, or skip if no German locale is installed."""

    original = locale.setlocale(locale.LC_TIME)
    for name in GERMAN_LOCALES:
        try:
            locale.setlocale(locale.LC_TIME, name)
            break
        except locale.Error:
            continue
    else:
        pytest.skip("no German locale installed")
    yield
    locale.setlocale(locale.LC_TIME, original)


def test_results_do_not_depend_on_the_locale(german_time_locale):
    """English month names and AM/PM parse under a German ``LC_TIME`` (PS-8, CV-7)."""

    assert convert_date_time("17 Jul 10:00") == "2026-07-17 10:00:00"
    assert convert_date_time("Today 02:00 PM") == "2026-05-13 14:00:00"
    assert convert_date_time("17/07 10:15 pm") == "2026-07-17 22:15:00"


def test_clock_24_and_12_hour():
    """24-hour input is read as is. With AM/PM it is read as 12-hour, in any case."""

    cases = [
        (("14:30", None), (14, 30)),
        (("00:00", None), (0, 0)),
        (("02:30", "PM"), (14, 30)),
        (("12:00", "AM"), (0, 0)),
        (("12:00", "PM"), (12, 0)),
        (("09:15", "am"), (9, 15)),
    ]
    for (time, am_pm), (hour, minute) in cases:
        result = convert_to_24_format(time=time, am_pm=am_pm)
        assert (result.hour, result.minute) == (hour, minute), (time, am_pm)


def test_clock_errors_name_the_input_and_the_format():
    """An unparseable time raises ``ClockFormatError`` saying which clock it expected."""

    with pytest.raises(ClockFormatError, match=r"cannot parse '25:00' as a 24-hour time \(HH:MM\)"):
        convert_to_24_format(time="25:00")
    with pytest.raises(ClockFormatError, match=r"cannot parse '13:00PM' as a 12-hour time \(HH:MM AM/PM\)"):
        convert_to_24_format(time="13:00", am_pm="pm")
    with pytest.raises(ClockFormatError, match=r"cannot parse '00:30AM' as a 12-hour time"):
        convert_to_24_format(time="00:30", am_pm="AM")
    with pytest.raises(ClockFormatError, match=r"cannot parse '10:30XM' as a 12-hour time"):
        convert_to_24_format(time="10:30", am_pm="xm")


def test_name_matches_abbreviations_and_partial_names():
    """The closest reference entry wins, ignoring case and punctuation."""

    teams = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets"]
    cases = [
        ("Mon", DAYS, "Monday"),
        ("tues", DAYS, "Tuesday"),
        ("Jul", MONTHS, "July"),
        ("Sept", MONTHS, "September"),
        ("A. Hawks", teams, "Atlanta Hawks"),
        ("Nets", teams, "Brooklyn Nets"),
        ("Celts", teams, "Boston Celtics"),
    ]
    for name, reference, expected in cases:
        assert convert_name(name=name, reference=reference) == expected, name


def test_name_cutoff_is_opt_in():
    """With no cutoff, the best entry always wins. With one, a poor match raises (CV-1)."""

    assert convert_name(name="zzz", reference=DAYS) == "Today"
    assert convert_name(name="Mon", reference=DAYS, score_cutoff=80) == "Monday"
    with pytest.raises(FuzzyMatchError, match="found no result for 'zzz'"):
        convert_name(name="zzz", reference=DAYS, score_cutoff=80)


def test_name_with_empty_reference_raises():
    """Nothing to match against raises ``FuzzyMatchError``, from a list or an empty generator."""

    with pytest.raises(FuzzyMatchError, match="in a reference list of 0 items"):
        convert_name(name="Mon", reference=[])
    with pytest.raises(FuzzyMatchError, match="in a reference list of 0 items"):
        convert_name(name="Mon", reference=iter([]))


def test_name_reference_of_any_iterable():
    """A generator or a tuple works like a list (CV-2)."""

    assert convert_name(name="Mon", reference=(day for day in DAYS)) == "Monday"
    assert convert_name(name="Jul", reference=tuple(MONTHS)) == "July"


def test_name_with_a_reference_that_is_not_iterable_raises_typed():
    """A reference that can't be iterated raises ``InvalidReferenceError``, never a bare ``TypeError`` (CV-2)."""

    with pytest.raises(InvalidReferenceError, match="expected an iterable of names, got NoneType: None"):
        convert_name(name="Mon", reference=None)  # pyrefly: ignore  # Deliberate wrong type
    with pytest.raises(InvalidReferenceError, match="expected an iterable of names, got str: 'Monday'"):
        convert_name(name="Mon", reference="Monday")  # A string is one name, not a list (CV-12)
