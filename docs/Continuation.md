# Continuation Doc: convi-lab

**Purpose:** self-contained context for continuing convi-lab in a fresh
conversation. Read it cold and pick up from "Next immediate action" at the
bottom. This doc owns the roadmap, the changes per version, locked-in
decisions, and what is built and what isn't. The rules live in
`Standards_and_Tracker.md`. Every finding ID used here (`PS-1`, `KN-1` and so
on) is defined in `Cleanliness_Tracker.md`.

**Last updated:** 2026-10-26

---

## 1. Where convi-lab sits

- **convi-lab** (`v0.1.1`, Python ≥ 3.10, dependencies `logger-lab` and
  `rapidfuzz`): turns messily formatted date and time strings into one
  `"YYYY-MM-DD HH:MM:SS"` string, with fuzzy name matching as a primitive. See
  the API Reference.
- **arbi-core is the main consumer, and the reason convi-lab exists.** It is
  Project_A's `packages/core`. Its scraper calls `convert_date_time()` on the
  first 10 characters of each scraped row (always `dd/mmHH:MM`, like
  `"27/1019:30"`), and `convert_name()` for team names, cached per league.

  | Project | Pin | Locked at | Uses |
  |---|---|---|---|
  | Project_A (`packages/core`, arbi-core) | `convi-lab>=0.1.0` | 0.1.0 | `convert_date_time`, `convert_name` |
  | ML_Project_Arbitrage | `convi-lab>=0.1.0` | 0.1.0 | `convert_date_time`, `convert_name` |

  Both import from the top level only. Project_A is already on logger-lab
  0.2.0. ML_Project_Arbitrage is locked to logger-lab **0.1.1** and uses its
  API (`lab, ProfileType`). Upgrading it to convi-lab 0.1.1 pulls in
  logger-lab 0.2.0, so it needs logger-lab's migration (logger-lab
  `Continuation.md` §2) at the same time.
- **arbi-core's installed convi-lab is hand-patched (`PK-7`, found
  2026-10-26).** The published 0.1.0 doesn't import with logger-lab 0.2.0
  (`logger_lab.main`), and Project_A pins 0.2.0. Its venv works only because
  `logging_config.py` was added to the installed copy and 7 files edited, which
  also altered uv's cached 0.1.0 through hardlinks. Any reinstall breaks
  arbi-core at import until 0.1.1 is published and pinned (Phase 3), and the
  cache is cleaned (`uv cache clean convi-lab`).
- **Noticed in arbi-core, not changed there:** `Scraping.build_event()`
  checks `event_date is None`, but `convert_date_time()` returns `""` on
  failure, never `None`. A row whose date fails is kept with an empty date
  instead of being dropped. That's arbi-core's code, so it's only noted here.

---

## 2. Built

| Area | Status | Notes |
| --- | --- | --- |
| `convert_date_time()`, the safe boundary | **Done** | Six shapes, any whitespace, any case, `""` on any failure, one log line per failure. |
| Parsers and `process_patterns()` | **Done 2026-10-26** | One clock read per conversion; `today=` on each parser; locale-free. |
| The year boundary rule, `resolve_date()` | **Done 2026-10-26** | A given year is exact; otherwise the next occurrence, Feb 29 included. |
| `convert_name()` | **Done** | Any iterable; opt-in `score_cutoff`; typed errors. |
| `convert_to_24_format()` | **Done** | 12- and 24-hour, locale-free. |
| Error hierarchy (`ConviError` …) | **Done** | Three classes reserved (`KN-2`). |
| logger-lab 0.2.0, one package logger | **Done 2026-10-26** | `convi_lab`, WARNING to stderr; module loggers propagate to it. |
| Packaging (`uv_build`, metadata, `py.typed`, `__version__`) | **Done 2026-10-26** | |
| Tests + type check | **Done 2026-10-26** | 37 tests on a frozen clock; pyrefly clean; Python 3.10, 3.13, 3.14. |
| Docs (`docs/`) | **Done 2026-10-26** | In logger-lab's shape. |
| Cleanliness round 1 | **Done 2026-10-26** | 7 of 7 passes closed. 13 bugs fixed. |

### 0.1.1 changes (2026-10-26)

The public changes since 0.1.0 (Standards §3.3). `from convi_lab import
convert_date_time, convert_name` works as before, and arbi-core gets the same
results on every input it has logged (`Cleanliness_Tracker.md`, "arbi-core
compatibility").

| Change | Breaking? | What a consumer does |
| --- | --- | --- |
| **A given year is kept** (`PS-1`). `"12.04.2025 22:15"` is 2025-04-12, not next year. | **Yes**, for dated inputs in the past | Nothing, if your inputs have no year (arbi-core's don't). |
| **Feb 29 without a year** is the next real Feb 29 (`PS-2`). It used to return `""`, or raise a bare `ValueError` from `process_patterns()`. | Fix | Nothing. |
| **More inputs convert**: any year (`KN-6`), one-digit days and months (`KN-7`), tabs and NBSP (`KN-5`), any case (`KN-11`), `Tues`/`Weds`/`Thurs`/`Thur`/`Sept` (`KN-12`). | New | Nothing. Inputs that used to give `""` now give a date. |
| **Made-up names are rejected**: `"17 Decuary"` returns `""` instead of a wrong date (`KN-13`). | Fix | Nothing. |
| **Locale-free**: month names and AM/PM no longer depend on `LC_TIME` (`PS-8`, `CV-7`). | Fix | Nothing. Apps with a non-English locale start converting. |
| **One clock read per conversion** (`PS-9`): correct across midnight on New Year's Eve. | Fix | Nothing. |
| `parse_date_time`, `parse_day_time`, `parse_day_month_time` take an optional `today=` | New | Nothing. |
| `process_patterns()` accepts spaced input; it no longer needs `remove_spaces()` first | New | Nothing. Compact input works as before. |
| `remove_spaces()` removes every kind of whitespace, not only `" "` | Behavior | Nothing, usually. |
| **`ConviError`** is the base error (`KN-10`). `LabError` stays as an alias. | New | Prefer `ConviError`. `except LabError` still works. |
| `InvalidReferenceError`: `convert_name()` with a reference it can't iterate (`CV-2`). It used to raise a bare `TypeError`. | New | Catch it, or `ConviError`. |
| `convert_name(..., score_cutoff=None)` (`CV-1`): opt in to a poor match raising `FuzzyMatchError` | New | Nothing. The default is unchanged. |
| `convert_name()` takes any iterable, generators included | New | Nothing. |
| `convert_name()` rejects a single string as the reference with `InvalidReferenceError` (`CV-12`). It used to match it letter by letter (`"Monday"` → `"M"`). | Fix | Pass a list of names. |
| `convert_date_time(pandas.NA)` returns `""` (`CV-10`). It raised `TypeError`, so `Series.map(convert_date_time)` crashed on a missing value. | Fix | Nothing. |
| **`TEST_CASES` removed** from the public API (`KN-3`) | **Yes** | Nobody known uses it. Copy the list if you need it. |
| `convi_lab.conversion_kernel` → `convi_lab.kernel` (D-1) | **Yes**, for deep imports | `from convi_lab.kernel.utils import remove_spaces`. |
| `process_patterns` moved from the kernel to `convi_lab.parsers` (`KN-8`) | **Yes**, for deep imports | `from convi_lab import process_patterns` (unchanged). |
| Kernel internals renamed or removed: `SHORTFORM_*`, `re_*`, `match_pattern`, `_test_pattern`; `parser_handler` moved to `convi_lab.parsers.parser_handler`; the modules' `test_case()` functions and `__main__` blocks | Removed | Nothing: they were internals and test helpers. |
| **Logging**: one logger-lab logger, `convi_lab`, WARNING to stderr. Module loggers propagate to it. One line per failure. Raising code doesn't log. (The published 0.1.0 imports `logger_lab.main`, so it doesn't import at all with logger-lab 0.2.0. arbi-core's hand-patched copy logs to the console at WARNING, one handler per module, and prints a failure twice: `PK-7`.) | Behavior | Nothing for arbi-core's console, except one line per failure instead of two. Change it with `logging.getLogger("convi_lab")`. |
| logger-lab `>=0.2.0,<0.3` (0.1.0 required `>=0.1.1`) | Packaging | An app pinned to logger-lab 0.1.x must migrate it too. |
| Installable with `uv_build`; `py.typed`; `convi_lab.__version__` (`PK-1`, `PK-2`) | New | Nothing. |

---

## 3. Roadmap

### Phase 1: 0.1.1 foundations: done 2026-10-26

Packaging, the `kernel` rename, the layering, the tests, the behavior-neutral
fixes and `docs/` (`Cleanliness_Tracker.md`, "Fixed before round 1").

### Phase 2: cleanliness round 1: done 2026-10-26

Review, then fixes in seven steps: regexes, date rules, locale, typed errors,
logging, API names, README and docs. Each step had tests that failed first,
and the arbi-core check after it.

### Phase 3: publish 0.1.1

1. The owner commits and pushes. (`.idea` is untracked and staged, `PK-5`.)
2. `uv build`, install the wheel in a clean venv and run it. Last done
   2026-10-26, at the end of round 1: it installs and runs on Python 3.10
   with warnings as errors.
3. Publish to PyPI when the owner says.
4. Project_A moves its pin to `convi-lab>=0.1.1,<0.2`, runs
   `uv cache clean convi-lab`, and relocks (`PK-7`). ML_Project_Arbitrage too,
   with its logger-lab migration (§1).

### Phase 4: new conversions

Kept here, moved from the README (`DOC-2`):

- **Number and currency:** locale-aware numbers (`"1.234,56"` DE,
  `"1,234.56"` US → `float`); currency strings (`"$1,200.00"`, `"€ 1.200"` →
  `Decimal`).
- **Identity and contact data:** phone numbers (`"+1 (800) 555-0100"` →
  E.164); emails (lowercase, strip display names, validate structure);
  personal names (`"DR. JOHN A. SMITH"` → prefix, first, last).
- **Units:** temperature (`"98.6 F"`, `"37 C"`, `"310 K"`), distance (km,
  miles, nautical miles), weight (kg, lb, oz).
- **Geolocation:** countries (`"USA"`, `"United States of America"` → ISO
  3166-1 alpha-2); time zones (`"EST"`, `"Eastern Time"` → IANA key).
- **Data quality:** booleans (`"yes"`, `"on"`, `"enabled"` → `bool`); null
  markers (`"N/A"`, `"none"`, `"–"` → `None`); invisible Unicode and line
  endings.

### For 0.2.0

- Decide the reserved errors (`KN-2`): raise `PatternMatchError` from
  `process_patterns()`, or remove all three.
- `convert_to_24_format()` returning a `time` (`CV-9`).
- A `datetime` result beside the string one (`Framework_Comparison.md`).

---

## 4. Decisions

| ID | Decision | Status |
| --- | --- | --- |
| D-1 | Name of the base package | **Locked in 2026-10-26 (owner):** `conversion_kernel` → `kernel`. |
| D-2 | Version for 0.1.1's changes | **Locked in 2026-10-26:** stays **0.1.1**. The top-level API is unchanged apart from `TEST_CASES`, and arbi-core gets the same results on its real inputs. |
| D-3 | Where tests live | **Locked in 2026-10-26 (owner):** in `tests/`, not in the modules. |
| D-4 | Order of work for 0.1.1 | **Locked in 2026-10-26 (owner):** behavior-neutral fixes first, then the cleanliness passes, each fix a recommendation with what it changes. |
| D-5 | How a library should log | **Locked in 2026-10-26 (owner approved the recommendation):** one logger-lab logger for the package, `convi_lab`, still printing WARNING and above, so arbi-core's console looks the same. Module loggers propagate to it. Only the boundary logs. |
| D-6 | What a given past year means | **Locked in 2026-10-26 (owner):** kept as given. |
| D-7 | What `"29/02"` without a year means | **Locked in 2026-10-26 (owner):** the next real Feb 29. |
| D-8 | Compatibility with arbi-core | **Locked in 2026-10-26 (owner):** arbi-core is the main consumer. A parsing change is checked against its real inputs before release (Standards §4). |

---

## 5. Next immediate action

The repo is ready to commit and push: round 1 and the final pass are done
(`Cleanliness_Tracker.md`), and the checks pass.

1. **Owner:** says when to commit and push. Everything is staged on `main`
   (45 files, `.idea` untracked, `PK-5`), and `main` is level with
   `origin/main`, so the push is a fast-forward. Nothing is committed yet.
2. **Owner:** publishes 0.1.1 (Phase 3).
3. Then Project_A: pin `convi-lab>=0.1.1,<0.2`, run `uv cache clean
   convi-lab`, relock and sync (`PK-7`). Rerun its suite: expect 305 passed
   and the same 2 unrelated failures (`test_megatron.py`, `PASS`/`FAIL` cases).
