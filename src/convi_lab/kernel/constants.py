"""
constants.py: the name tables, the regex fragments and the compiled ``TIME_PATTERNS`` the parsers match against.

Whitespace of any kind is allowed between the parts of an input, and the
compact form (no spaces at all) matches too. Day and month names match in any
case. Where a compact input could be read two ways, two-digit numbers win:
``"1/111:00"`` is November 1st at 01:00.
"""

import re

###########################
# Day / month name tables #
###########################

# All available days for the day time parser
DAYS = [
    'Today', 'Tomorrow', 'Monday', 'Tuesday',
    'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]

# All calendar months for pattern parsers
MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Relative days, resolved by parse_day_time's relative_day()
RELATIVE_DAYS = [
    'Today', 'Tomorrow'
]

# Map days to datetime standard
WEEKDAY_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}

#####################################################
# Accepted short forms (each name's own, no others) #
#####################################################

# The short forms of each day, besides its full name
DAY_SHORT_FORMS = {
    'Monday': ['Mon'],
    'Tuesday': ['Tue', 'Tues'],
    'Wednesday': ['Wed', 'Weds'],
    'Thursday': ['Thu', 'Thur', 'Thurs'],
    'Friday': ['Fri'],
    'Saturday': ['Sat'],
    'Sunday': ['Sun'],
}

# The short forms of each month, besides its full name
MONTH_SHORT_FORMS = {
    'January': ['Jan'], 'February': ['Feb'], 'March': ['Mar'], 'April': ['Apr'],
    'May': [], 'June': ['Jun'], 'July': ['Jul'], 'August': ['Aug'],
    'September': ['Sep', 'Sept'], 'October': ['Oct'], 'November': ['Nov'], 'December': ['Dec'],
}

# Every accepted spelling, longest first so "Tuesday" is tried before "Tue"
DAY_SPELLINGS = sorted(
    DAYS + [form for forms in DAY_SHORT_FORMS.values() for form in forms], key=len, reverse=True
)
MONTH_SPELLINGS = sorted(
    MONTHS + [form for forms in MONTH_SHORT_FORMS.values() for form in forms], key=len, reverse=True
)

###################
# Regex fragments #
###################

SEP_RE = r"\s*"  # Optional whitespace between two parts
DAY_NUMBER_RE = r"(?:3[01]|[12][0-9]|0?[1-9])"  # 1 to 31, two digits tried first
MONTH_NUMBER_RE = r"(?:1[0-2]|0?[1-9])"  # 1 to 12, two digits tried first
DATE_SEPARATOR_RE = rf"{SEP_RE}[./]{SEP_RE}"  # "/" or ".", with optional whitespace around it
YEAR_RE = r"(\d{4}|\d{2})"  # Captured: a 2- or 4-digit year
TIME_RE = rf"((?:[01]?\d|2[0-3]){SEP_RE}:{SEP_RE}[0-5]\d)"  # Captured: H:MM or HH:MM, 24-hour range
AM_PM_RE = rf"{SEP_RE}([ap]m)?$"  # Captured: an optional AM/PM, at the end
DAY_NAME_RE = rf"({'|'.join(DAY_SPELLINGS)})"  # Captured: a day name or short form
MONTH_NAME_RE = rf"({'|'.join(MONTH_SPELLINGS)})"  # Captured: a month name or short form
DATE_RE = rf"({DAY_NUMBER_RE}{DATE_SEPARATOR_RE}{MONTH_NUMBER_RE})"  # Captured: day and month, as written
OPTIONAL_YEAR_RE = rf"(?:{DATE_SEPARATOR_RE}{YEAR_RE})?"  # The year with its separator, if there is one

#####################
# Compiled patterns #
#####################

# Event_data patterns, tried in this order. Groups: see each parser's docstring.
TIME_PATTERNS: dict[str, re.Pattern] = {
    # "Tuesday 12:30 AM", "today 20:00", "Tues12:30"
    'day_time': re.compile(
        rf'^{DAY_NAME_RE}{SEP_RE}{TIME_RE}{AM_PM_RE}', re.IGNORECASE
    ),
    # "17 Jul - 02:00 PM", "7JUL14:00"
    'day_month_time': re.compile(
        rf'^({DAY_NUMBER_RE}){SEP_RE}{MONTH_NAME_RE}{SEP_RE}-?{SEP_RE}{TIME_RE}{AM_PM_RE}', re.IGNORECASE
    ),
    # "12/04 23:15", "31.08.2025 03:15 AM", "27/1019:30"
    'datetime': re.compile(
        rf'^{DATE_RE}{OPTIONAL_YEAR_RE}{SEP_RE}{TIME_RE}{AM_PM_RE}', re.IGNORECASE
    ),
}
