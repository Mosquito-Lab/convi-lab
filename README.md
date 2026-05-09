# convi-lab

Data conversion and normalization utilities. The current focus is datetime
parsing — turning messily formatted date/time strings into a single
normalized `"YYYY-MM-DD HH:MM:SS"` output — with fuzzy name matching as a
first-class primitive that powers the date logic and is exposed for general use.

---

## Installation

```bash
pip install convi-lab
```

**Runtime dependencies:** `logger-lab >= 0.1.1`, `rapidfuzz >= 3.0.0`

---

## Quick start

```python
from convi_lab import convert_date_time, convert_name, DAYS, MONTHS

# Datetime normalization
convert_date_time("Tuesday 12:30 PM")      # "2026-05-13 12:30:00"
convert_date_time("17 Jul - 02:00 PM")     # "2026-07-17 14:00:00"
convert_date_time("12.04.2025 22:15")      # "2026-04-12 22:15:00"
convert_date_time("Today 09:00")           # "2026-05-09 09:00:00"

# Fuzzy name matching
convert_name("Mon",    DAYS)               # "Monday"
convert_name("Jul",    MONTHS)             # "July"
convert_name("Celts",  ["Boston Celtics", "Brooklyn Nets"])  # "Boston Celtics"
```

---

## Supported datetime formats

All formats accept an optional `AM`/`PM` suffix (case-insensitive).
Spaces between components are stripped automatically.

| Format                 | Example input           | Parsed as            |
|------------------------|-------------------------|----------------------|
| `dd/mm HH:MM`          | `"12/04 22:15"`         | April 12, 22:15      |
| `dd/mm/yy HH:MM`       | `"12/04/25 10:15 PM"`   | April 12 2025, 22:15 |
| `dd.mm.yyyy HH:MM`     | `"12.04.2025 12:15 pm"` | April 12 2025, 12:15 |
| `Day HH:MM`            | `"Tuesday 12:30"`       | Next Tuesday, 12:30  |
| `Today/Tomorrow HH:MM` | `"Today 14:30"`         | Today at 14:30       |
| `ddMon[-]HH:MM`        | `"17 Jul - 02:00 PM"`   | July 17, 14:00       |

**Year boundary rule:** if the resolved date is in the past (date only,
not time), the year is automatically bumped to the next calendar year.

**Day rule:** weekday names always resolve to the *next* occurrence. If
today is Tuesday and you pass `"Tuesday 12:30"`, the result is next
Tuesday, not today.

---

## Error handling

All exceptions inherit from `LabError`. You can catch broadly or precisely:

```python
from convi_lab import convert_date_time, LabError, ParserError

# convert_date_time is the safe boundary — it returns "" on any failure
result = convert_date_time("garbage input")
assert result == ""

# Call process_patterns directly to get typed exceptions
from convi_lab import process_patterns
from convi_lab.conversion_kernel.utils import remove_spaces

try:
    dt = process_patterns(remove_spaces("17 Jly - 02:00"))
except ParserError as exc:
    print(f"Parse failed: {exc}")
except LabError as exc:
    print(f"Conversion failed: {exc}")
```

### Exception hierarchy

```
LabError
├── ParserError
│   ├── PatternMatchError      no pattern matched the input
│   ├── DayResolutionError     weekday/relative-day string unresolvable
│   ├── MonthResolutionError   month name unresolvable
│   └── DateComponentError     numeric date fragment malformed
└── ConversionError
    ├── ClockFormatError       HH:MM[AM|PM] string failed to parse
    ├── FuzzyMatchError        rapidfuzz returned no result
    └── InvalidInputError      bad type or empty string at entry point
```

---

## Fuzzy name matching

`convert_name` is a general-purpose utility — pass any query and any
reference list:

```python
from convi_lab import convert_name

teams = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets"]
convert_name("A. Hawks", teams)   # "Atlanta Hawks"
convert_name("Nets",     teams)   # "Brooklyn Nets"

countries = ["United States", "United Kingdom", "Australia"]
convert_name("USA",   countries)  # "United States"
convert_name("Aus",   countries)  # "Australia"
```

It raises `FuzzyMatchError` if rapidfuzz finds nothing, so you always
get a typed failure rather than a silent empty string.

---

## Roadmap

The library is intentionally small today. Planned additions:

### Number and currency
- **Locale-aware number parsing** — `"1.234,56"` (DE) / `"1,234.56"` (US) → `float`
- **Currency string normalization** — `"$1,200.00"`, `"€ 1.200"` → `Decimal`

### Identity and contact data
- **Phone number normalization** — `"+1 (800) 555-0100"`, `"08001234"` → E.164 format
- **Email normalization** — lowercase, strip display names, validate structure
- **Name normalization** — `"DR. JOHN A. SMITH"` → `{"prefix": "Dr.", "first": "John", "last": "Smith"}`

### Units and measurements  
- **Temperature** — `"98.6 F"` / `"37 C"` / `"310 K"` → normalized `(value, unit)`
- **Distance** — km, miles, nautical miles with conversion helpers
- **Weight** — kg, lb, oz

### Geolocation
- **Country/locale normalization** — `"USA"`, `"US"`, `"United States of America"` → ISO 3166-1 alpha-2
- **Timezone string normalization** — `"EST"`, `"Eastern Time"`, `"America/New_York"` → IANA key

### Data quality
- **Boolean parsing** — `"yes"`, `"true"`, `"1"`, `"on"`, `"enabled"` → `bool`
- **Null/empty detection** — `"N/A"`, `"none"`, `"–"`, `""` → `None`
- **Whitespace and encoding normalization** — strip invisible Unicode, normalize line endings

---

## License

MIT — see [LICENSE](LICENSE).
