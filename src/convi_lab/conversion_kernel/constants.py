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

# Relative days specific to parse_relative_time()
RELATIVE_DAYS = [
    'Today','Tomorrow'
]

# Map days to datetime standard
WEEKDAY_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}

###############################################
# Abbreviation tables (used to build regexes) #
###############################################

# Day abbreviations
SHORTFORM_DAYS = [
    'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
]

# Month abbreviations
SHORTFORM_MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

# The remaining part of day abbreviations
SHORTFORM_DAY_ENDERS = [
    'day', 'sday', 'nesday', 'rsday', 'urday'
]


# The remaining part of month abbreviations
SHORTFORM_MONTH_ENDERS = [
    'uary', 'ruary', 'ch', 'il',
    'y', 'ust', 'tember', 'ober', 'ember',
    'e'
]

##########################
# Atomic regex fragments #
##########################

# Date regular expressions
re_num_day = r"^(?:0[0-9]|[12][0-9]|3[01])"
re_num_month = r"[./](?:0[1-9]|1[0-2])"
re_year = r"([./]2[5-9]|[./]202[5-9])?"

# Time regular expressions
re_time = r"((?:[01]?\d|2[0-3]):[0-5]\d)"
re_am_pm = r"([AaPp][Mm])?$"

######################
# Compound fragments #
######################

# Compound regular expressions
_date_re = rf"({re_num_day}{re_num_month})"
_day_re = rf"^((?:Today|Tomorrow|{'|'.join(SHORTFORM_DAYS)})(?:{'|'.join(SHORTFORM_DAY_ENDERS)})?)"
_month_re = rf"((?:{'|'.join(SHORTFORM_MONTHS)})(?:{'|'.join(SHORTFORM_MONTH_ENDERS)})?)"

#####################
# Compiled patterns #
#####################

# "12/04/2523:15", "31/08/202503:15AM"
_datetime_pattern = re.compile(rf'{_date_re}{re_year}{re_time}{re_am_pm}') # "12/04/2523:15", "31/08/202503:15AM"

# "Tuesday12:30AM", "Today20:00"
_day_time_pattern = re.compile(rf'{_day_re}{re_time}{re_am_pm}') # "Tuesday12:30AM", "Today20:00

# "17Jul-02:00PM"
_day_month_time_pattern = re.compile(rf'^(0[0-9]|[12][0-9]|3[01]){_month_re}-?{re_time}{re_am_pm}') # "17Jul-02:00PM"


# Event_data patterns (all without spaces)
TIME_PATTERNS: dict[str, re.Pattern] = {
    'day_time': _day_time_pattern,
    'day_month_time': _day_month_time_pattern,
    'datetime': _datetime_pattern
}

#################
# Test fixtures #
#################

# Unit test cases
TEST_CASES = [
        "12/04 22:15",  # 24-hour, no AM/PM, with space
        "12/04 10:15 PM",  # 12-hour with PM, with spaces
        "Tuesday 12:30",  # 24-hour weekday, with space
        "Tuesday 12:30 PM",  # 12-hour weekday, with space
        "12.04.2025 12:15",  # 24-hour full date, with space
        "12.04.2025 12:15 pm",  # 12-hour full date, with spaces
        "Tuesday 02:30 PM",  # 12-hour with space
        "17 Jul - 02:00",  # 24-hour with month, with spaces
        "17 Jul - 02:00 PM",  # 12-hour with month, with spaces
        "Today 14:30",  # 24-hour today, with space
        "Tomorrow 03:30 PM",  # 12-hour tomorrow, with space
        # No-space versions
        "12/0422:15",
        "Tuesday12:30PM",
        "17Jul-02:00PM",
        "Wed1:30am"
    ]
