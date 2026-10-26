# convi-lab: Framework Comparison and Capability Map

## Purpose and scope

convi-lab is a **narrow normalizer**, not a general date parser. It reads a
closed set of compact date/time shapes, the kind found in scraped event
listings (`"17Jul-02:00PM"`, `"Tue 12:30"`, `"12/04 22:15"`), and returns one
string format. Its rules lean toward the future: a listing's date without a
year is the next one, and a weekday is the next one.

This assessment is based on the **0.1.1** source tree at the end of cleanliness round 1 (2026-10-26). "Missing"
means *not provided by convi-lab itself*. Nothing here was benchmarked.

## What convi-lab provides today

| Area | Current provision | Status |
| --- | --- | --- |
| One safe entry point | `convert_date_time()` returns `"YYYY-MM-DD HH:MM:SS"` or `""`, never raises, logs one line per failure | Available |
| Typed errors underneath | `process_patterns()` and the conversions raise `ConviError` subclasses, never bare built-in errors | Available (0.1.1) |
| Forgiving input | Whitespace of any kind optional between parts; names in any case; 1–2 digit days and months; any 2- or 4-digit year | Available (0.1.1) |
| Future-leaning rules | A date without a year is its next occurrence (Feb 29 included); weekdays are the next one; Today/Tomorrow. A given year is kept | Available (0.1.1) |
| Short forms | `Tue`/`Tues`, `Thu`/`Thur`/`Thurs`, `Sep`/`Sept` …, each name's own only | Available (0.1.1) |
| Locale-free | Month names and AM/PM don't depend on `LC_TIME` | Available (0.1.1) |
| Fuzzy matching as a tool | `convert_name()` over any iterable, with an opt-in `score_cutoff` | Available |
| 12/24-hour clock | `convert_to_24_format()` | Available |

## How it compares

| Library | What it does | Against convi-lab |
| --- | --- | --- |
| stdlib `datetime.strptime` | One known format per call | convi-lab tries several shapes and applies the date rules. `strptime` is the right tool when the format is known. |
| `python-dateutil` (`parser.parse`) | Parses most human-written formats. Missing parts come from a default date. `dayfirst` and `fuzzy` options | Far broader. It doesn't read `Today`/`Tomorrow`, and it doesn't move a past date forward. It handles time zones and ISO 8601, which convi-lab doesn't. |
| `dateparser` | Natural language and relative dates (`"in 2 days"`) in many languages, with a setting to prefer future dates | The closest in intent, and far broader. It is a heavier dependency, and slower than matching a few regexes. convi-lab is English-only and covers a fixed set of shapes. |
| `arrow`, `pendulum` | Better datetime types, with parsing by format tokens | You give them the format. convi-lab finds it among its own. |
| `rapidfuzz`, `thefuzz` | Fuzzy string matching | `convert_name()` is a thin wrapper over rapidfuzz's `extractOne`, with a typed error. |

## Gap assessment

Round 1 (2026-10-26) fixed the correctness gaps: years from 2030, single
digits, letter case, short forms, the locale, Feb 29, the year boundary and
the clock read (`Cleanliness_Tracker.md`). What's left is scope:

1. **Output is a string.** Callers that want a `datetime` must parse the
   result again, or call `process_patterns()` and handle its errors.
2. **No time zones, seconds or ISO 8601 input.** Results are naive local
   times.
3. **English only.** Day and month names are English.
4. **No relative expressions** beyond Today and Tomorrow (`"in 2 days"`).

## Recommended implementation order

These are proposals, not decisions.

1. Offer a `datetime` result beside the string one.
2. ISO 8601 input and seconds, if a consumer needs them.
3. Settle the reserved errors in 0.2.0 (`KN-2`).
4. The new conversions on the roadmap (`Continuation.md` §3, Phase 4).

## Design boundary to preserve

- **A closed list of formats, each one tested.** A new shape is added on
  purpose (Standards §3.1), not guessed at.
- **One safe boundary, typed errors below it.** Consumers who want `""` get
  it. Consumers who want to know why can ask.
- **Small dependencies.** rapidfuzz and logger-lab only.
