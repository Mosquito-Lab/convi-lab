# convi-lab API Reference

**Documentation snapshot: 2026-10-26, version 0.1.1**

## Scope and import policy

Import from the top level:

```python
from convi_lab import convert_date_time, convert_name, ConviError
```

Everything in `convi_lab.__all__` is public. The subpackages export their own
layer's tools (`convi_lab.kernel`, `convi_lab.conversions`,
`convi_lab.parsers`). Anything reached by a deeper path is internal and may
move between versions (see `Continuation.md`, 0.1.1 changes).

| Group | Names |
|---|---|
| Conversions | `convert_date_time`, `convert_name`, `convert_to_24_format` |
| Parsers | `process_patterns`, `parse_date_time`, `parse_day_time`, `parse_day_month_time` |
| Errors | `ConviError` (alias `LabError`), `ParserError`, `ConversionError` and their subclasses (below) |
| Constants | `DAYS`, `MONTHS`, `RELATIVE_DAYS`, `WEEKDAY_MAP`, `TIME_PATTERNS` |
| Version | `__version__` |

---

## `convert_date_time(event_date) -> str`

The entry point. Turns a raw date/time string into `"YYYY-MM-DD HH:MM:SS"`.

- **Never raises.** A bad type (`None`, a number, `pandas.NA`), an empty
  string, unmatched input or an impossible date logs one line and returns
  `""`.
- **Whitespace between parts is optional**, and can be any kind (spaces,
  tabs, non-breaking spaces). `"17 Jul - 02:00 PM"` and `"17Jul-02:00PM"` are
  the same input. Only the ends are trimmed: spaces are never deleted before
  matching.
- **Names match in any case**: `"monday"`, `"MON"`, `"17 JUL"`.
- **AM/PM is optional**, in any case. Without it, the time is read as 24-hour.
- **The locale doesn't matter.** Month names and AM/PM are read by the
  library, not by the system locale.

### Supported formats

| Format | Examples | Pattern name |
|---|---|---|
| `d/m HH:MM` (or `d.m`) | `"12/04 22:15"`, `"7/6 9:00"`, `"27/1019:30"` | `datetime` |
| `d/m/yy HH:MM` | `"12/04/26 10:15 PM"` | `datetime` |
| `d.m.yyyy HH:MM` | `"12.04.2026 12:15 pm"` | `datetime` |
| `Day HH:MM` | `"Tuesday 12:30"`, `"Tues 12:30"`, `"mon 12:30"` | `day_time` |
| `Today/Tomorrow HH:MM` | `"Today 14:30"`, `"tomorrow 9:00"` | `day_time` |
| `d Mon[-]HH:MM` | `"17 Jul - 02:00 PM"`, `"7 Sept 10:00"`, `"17 JULY 14:00"` | `day_month_time` |

- Days and months take one or two digits. Years take two or four. A two-digit
  year reads like `strptime`'s `%y`: `00`–`68` are 2000–2068, `69`–`99` are
  1969–1999.
- Day short forms (`DAY_SHORT_FORMS`): `Mon`, `Tue`/`Tues`, `Wed`/`Weds`,
  `Thu`/`Thur`/`Thurs`, `Fri`, `Sat`, `Sun`. Month short forms
  (`MONTH_SHORT_FORMS`): the first three letters, plus `Sept`. A name with
  another name's ending (`"Decuary"`) doesn't match.
- **Compact input:** where digits could be read two ways, two-digit numbers
  win. `"1/111:00"` is November 1 at 01:00. Spaced input is never ambiguous:
  `"1/1 11:00"` is January 1 at 11:00.
- Seconds, ISO 8601 and time zones aren't supported.

### Date rules

Results depend on today's date. The clock is read once per conversion.

| Rule | Behavior | Example, on Wednesday 2026-05-13 |
|---|---|---|
| No year | The next occurrence on or after today's date | `"17/07 10:00"` → `"2026-07-17 10:00:00"` |
| | A date already past this year is next year's | `"17/01 09:00"` → `"2027-01-17 09:00:00"` |
| | Today's date at an earlier hour stays today | `"13/05 08:00"` → `"2026-05-13 08:00:00"` |
| | Feb 29 is the next leap year's | `"29/02 10:00"` → `"2028-02-29 10:00:00"` |
| Year given | Exactly that date, even in the past | `"12.04.2025 22:15"` → `"2025-04-12 22:15:00"` |
| | A year without that date is `""` | `"29/02/2027 10:00"` → `""` |
| Weekday | The next occurrence. Today's own weekday means a week from today | `"Wednesday 12:00"` → `"2026-05-20 12:00:00"` |
| Today / Tomorrow | Today's or tomorrow's date | `"Tomorrow 03:30 PM"` → `"2026-05-14 15:30:00"` |

---

## `process_patterns(event_date) -> datetime | None`

The parser dispatcher, for callers who want typed errors instead of `""`.

- *event_date* must be trimmed at both ends. Whitespace between parts is
  optional, as in `convert_date_time()`.
- Reads the clock once, then tries each pattern in `TIME_PATTERNS`, in order
  (`day_time`, `day_month_time`, `datetime`), and hands the first match to its
  parser (`PATTERN_HANDLERS`).
- Returns `None` when nothing matches.
- Raises `DateComponentError` for an impossible date (`"31/02 10:00"`) and
  `ClockFormatError` for an impossible time (`"Today 13:00 PM"`). It never
  raises a bare `ValueError`.

```python
from convi_lab import process_patterns, ParserError

try:
    when = process_patterns("31/02 10:00")
except ParserError as exc:
    print(f"Parse failed: {exc}")   # date fragment '31.02' is malformed: day is out of range for month
```

### The parsers

`parse_date_time(match, today=None)`, `parse_day_time(match, today=None)` and
`parse_day_month_time(match, today=None)` each take the `re.Match` of their
own pattern in `TIME_PATTERNS` and return a `datetime`. *today* is the moment
to treat as now. `None` reads the clock once. They all end in
`parser_handler()`, whose `resolve_date()` applies the date rules above.

```python
from datetime import datetime
from convi_lab import TIME_PATTERNS, parse_date_time

match = TIME_PATTERNS["datetime"].match("05/01 10:00")
parse_date_time(match, today=datetime(2026, 12, 31))   # datetime(2027, 1, 5, 10, 0)
```

---

## `convert_name(name, reference, score_cutoff=None) -> str`

Fuzzy matching with rapidfuzz's `extractOne` (scorer WRatio,
`default_process`: lowercased, punctuation stripped).

```python
from convi_lab import convert_name, DAYS

convert_name(name="Mon", reference=DAYS)                                     # "Monday"
convert_name(name="Celts", reference=["Boston Celtics", "Brooklyn Nets"])   # "Boston Celtics"
```

- *reference* can be any iterable: a list, a tuple, a dict (its values are
  matched), a generator.
- **By default there is no score cutoff.** A non-empty reference always
  returns its best entry: `convert_name(name="zzz", reference=DAYS)` returns
  `"Today"`. Pass `score_cutoff` (0 to 100) to make a poor match raise
  `FuzzyMatchError`.
- An empty reference raises `FuzzyMatchError`. A single string (which would
  be matched letter by letter) or a reference that can't be iterated (`None`)
  raises `InvalidReferenceError`.
- It doesn't log. The caller decides what to do with the error.

---

## `convert_to_24_format(time, am_pm=None) -> datetime`

Reads `"HH:MM"` as a 24-hour time, or as a 12-hour time (hours 1 to 12) when
*am_pm* is `"AM"` or `"PM"`, in any case. Returns a `datetime` on 1900-01-01
carrying the time. Raises `ClockFormatError` naming the input and the clock it
expected. It doesn't depend on the locale, and doesn't log.

```python
convert_to_24_format(time="02:30", am_pm="PM")   # datetime(1900, 1, 1, 14, 30)
convert_to_24_format(time="25:00")               # ClockFormatError: cannot parse '25:00' as a 24-hour time (HH:MM)
```

---

## Constants

| Name | What |
|---|---|
| `DAYS` | `Today`, `Tomorrow`, then Monday to Sunday: the names `parse_day_time` matches against |
| `MONTHS` | January to December. A month's number is its index + 1 |
| `RELATIVE_DAYS` | `Today`, `Tomorrow` |
| `WEEKDAY_MAP` | Weekday name → `datetime.weekday()` number |
| `TIME_PATTERNS` | Pattern name → compiled regex (whitespace optional, any case) |

`kernel.constants` also holds `DAY_SHORT_FORMS`, `MONTH_SHORT_FORMS` and the
regex fragments. They're internal.

---

## Kernel

| Name | What |
|---|---|
| `kernel.remove_spaces(value)` | Removes every whitespace character |
| `kernel.build_logger(name)` | A module's logger: a child of `convi_lab`, with no handler of its own |
| `kernel.logging_config.PACKAGE_LOGGER` | The `convi_lab` logger, built once at import with logger-lab |

### Logging

convi-lab logs through one logger, `convi_lab`, built with logger-lab: a
console output at WARNING, on stderr, with `propagate = False`. Every module
logger (`convi_lab.parsers.parse_day_time` …) is its child, with no handler,
so each record is printed once.

- `convert_date_time()` logs one line per failure: WARNING for input that
  matches no pattern or isn't a non-empty string, ERROR for a parse or
  conversion error.
- Functions that raise don't log.
- Debug lines (which pattern matched, the captured parts) are off at WARNING.

To change what convi-lab prints, change that one logger:

```python
import logging

logging.getLogger("convi_lab").setLevel(logging.ERROR)   # hide unmatched-input warnings
```

---

## Errors

```text
ConviError                     (LabError is its old name, still accepted)
├── ParserError
│   ├── PatternMatchError      reserved: no pattern matched the input
│   ├── DayResolutionError     reserved: weekday/relative-day string unresolvable
│   ├── MonthResolutionError   reserved: month name unresolvable
│   └── DateComponentError     the day, month and year don't make a real date
└── ConversionError
    ├── ClockFormatError       HH:MM[AM|PM] string failed to parse
    ├── FuzzyMatchError        no match: empty reference, or below score_cutoff
    ├── InvalidInputError      bad type or empty string at the entry point
    └── InvalidReferenceError  convert_name's reference isn't a collection of names
```

| Error | Raised by | Message |
|---|---|---|
| `DateComponentError` | the `datetime` and `day_month_time` parsers | `date fragment '31.02' is malformed: day is out of range for month` |
| `ClockFormatError` | `convert_to_24_format()` | `cannot parse '13:00PM' as a 12-hour time (HH:MM AM/PM)` |
| `FuzzyMatchError` | `convert_name()` | `fuzzy match found no result for 'zzz' in a reference list of 9 items` |
| `InvalidReferenceError` | `convert_name()` | `expected an iterable of names, got str: 'Monday'` |
| `InvalidInputError` | nothing: `convert_date_time()` logs its message | `expected a non-empty str, got NoneType: None` |
| `PatternMatchError` | nothing: reserved. `convert_date_time()` logs its message | `'x' did not match any known pattern. Available patterns: day_time, day_month_time, datetime` |
| `DayResolutionError` | nothing: reserved | `'Xyz' could not be resolved to a weekday or relative day. Valid values: …` |
| `MonthResolutionError` | nothing: reserved | `'Jly' could not be resolved to a calendar month. Valid values: …` |

---

## Adding an input format

See `Standards_and_Tracker.md` §3.1.
