# convi-lab

Normalize messy date and time strings into one `"YYYY-MM-DD HH:MM:SS"` format.
Fuzzy name matching powers the date logic, and it's available on its own too.

---

## Installation

```bash
pip install convi-lab
```

**Runtime dependencies:** `logger-lab >= 0.2.0, < 0.3`, `rapidfuzz >= 3.0.0`

---

## Quick start

```python
from convi_lab import convert_date_time, convert_name, DAYS, MONTHS

# The results below assume today is Wednesday 2026-05-13
convert_date_time("Tuesday 12:30 PM")      # "2026-05-19 12:30:00"
convert_date_time("17 Jul - 02:00 PM")     # "2026-07-17 14:00:00"
convert_date_time("27/1019:30")            # "2026-10-27 19:30:00"
convert_date_time("12.04.2025 22:15")      # "2025-04-12 22:15:00"
convert_date_time("today 09:00")           # "2026-05-13 09:00:00"
convert_date_time("garbage")               # ""

convert_name(name="Mon", reference=DAYS)       # "Monday"
convert_name(name="Sept", reference=MONTHS)    # "September"
convert_name(name="Celts", reference=["Boston Celtics", "Brooklyn Nets"])   # "Boston Celtics"
```

---

## Supported datetime formats

Whitespace between the parts is optional and can be any kind (spaces, tabs,
non-breaking spaces). Day and month names match in any case. Every format
takes an optional `AM`/`PM`, in any case.

| Format | Examples | Result, if today is 2026-05-13 |
|---|---|---|
| `d/m HH:MM` (or `d.m`) | `"17/07 22:15"`, `"27/1019:30"` | 2026-07-17 22:15, 2026-10-27 19:30 |
| `d/m/yy HH:MM` | `"12/04/25 10:15 PM"` | 2025-04-12 22:15 |
| `d.m.yyyy HH:MM` | `"12.04.2025 12:15 pm"` | 2025-04-12 12:15 |
| `Day HH:MM` | `"Tuesday 12:30"`, `"Tues 12:30"`, `"MON 12:30"` | the next Tuesday or Monday, 12:30 |
| `Today/Tomorrow HH:MM` | `"Today 14:30"`, `"tomorrow 9:00"` | 2026-05-13 14:30, 2026-05-14 09:00 |
| `d Mon[-]HH:MM` | `"17 Jul - 02:00 PM"`, `"7 Sept 10:00"` | 2026-07-17 14:00, 2026-09-07 10:00 |

Days and months take one or two digits. Years take two or four: a two-digit
year reads like `strptime`'s `%y` (`00`–`68` are 2000–2068, `69`–`99` are
1969–1999). Short day names are `Mon`, `Tue`/`Tues`, `Wed`/`Weds`,
`Thu`/`Thur`/`Thurs`, `Fri`, `Sat`, `Sun`. Short month names are the first
three letters, plus `Sept`.

### Date rules

- **No year:** the date is its next occurrence on or after today. A date
  already past this year is next year's (`"17/01 09:00"` → 2027-01-17).
  February 29 is the next leap year's.
- **A year given:** exactly that date, even in the past.
- **Weekdays** are the next occurrence. If today is Tuesday, `"Tuesday 12:30"`
  is next Tuesday, not today.
- **Compact input:** where the digits could be read two ways, two-digit
  numbers win. `"1/111:00"` is November 1 at 01:00. Write `"1/1 11:00"` for
  January 1.
- Results don't depend on the system locale.

---

## Error handling

`convert_date_time` is the safe boundary: it never raises, and returns `""`
for anything it can't convert (`None`, a number, `pandas.NA`, unmatched text). For the reason, call `process_patterns`, which
raises typed errors. Every error inherits from `ConviError`.

```python
from convi_lab import convert_date_time, process_patterns, ParserError

convert_date_time("31/02 10:00")           # ""

try:
    process_patterns("31/02 10:00")
except ParserError as exc:
    print(f"Parse failed: {exc}")          # date fragment '31.02' is malformed: day is out of range for month

process_patterns("no date here")           # None: no pattern matched
```

### Exception hierarchy

```
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

"Reserved" errors are part of the API, but nothing raises them in 0.1.x.

---

## Fuzzy name matching

`convert_name` works with any query and any iterable of names:

```python
from convi_lab import convert_name

teams = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets"]
convert_name(name="A. Hawks", reference=teams)     # "Atlanta Hawks"
convert_name(name="Nets", reference=teams)         # "Brooklyn Nets"

countries = ["United States", "United Kingdom", "Australia"]
convert_name(name="USA", reference=countries)      # "United States"
convert_name(name="Aus", reference=countries)      # "Australia"
```

By default there is no score cutoff: it always returns the closest entry,
even when nothing is close (`convert_name(name="zzz", reference=teams)` still
returns a team). Pass `score_cutoff` (0 to 100) to make a poor match raise
`FuzzyMatchError` instead. An empty reference raises `FuzzyMatchError`. A
single string, or anything that can't be iterated, raises
`InvalidReferenceError`.

---

## Logging

convi-lab logs through one logger, `convi_lab`, built with logger-lab. It
prints WARNING and above to stderr: one line for each input
`convert_date_time` couldn't convert. Functions that raise don't log. To
change what convi-lab prints, change that one logger:

```python
import logging

logging.getLogger("convi_lab").setLevel(logging.ERROR)   # hide unmatched-input warnings
```

---

## Roadmap

Planned: numbers and currency, contact data (phone numbers, emails, personal
names), units, countries and time zones, and data-quality helpers (booleans,
null markers). The roadmap is kept in
[`docs/Continuation.md`](https://github.com/Mosquito-Lab/convi-lab/blob/main/docs/Continuation.md).

---

## License

MIT. See [LICENSE](LICENSE).
