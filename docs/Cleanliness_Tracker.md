# Cleanliness & Efficiency Tracker

This is the file-level review ledger for `convi_lab`. **Round 1 opened and
closed on 2026-10-26** at version **0.1.1**.

1. **Behavior-neutral fixes first** (owner, 2026-10-26): packaging, the
   `kernel` rename, the import layering, the tests, typing, truthful
   docstrings and house style.
2. **Review:** every file read in full against the checklist (owner: "go over
   all the files"). Every **bug** was reproduced with a real run: on a
   controlled clock where the date matters (2026-05-13, 2028-03-01, a clock
   that ticks over New Year), and under a German `LC_TIME` for the locale
   findings.
3. **Fixes** (owner: "I agree with all your recommendations. Just make sure it
   still works with arbi-core"): applied in the recommended order, each step
   with tests that failed before it. After every step, arbi-core's real inputs
   were run through the new code and compared with the convi-lab 0.1.0 it
   ships with (see "arbi-core compatibility" below).
4. **Final pass** (owner, 2026-10-26: "do one final cleanliness pass"): every
   file re-read in full, a house-style scan over every file, edge probes, and
   a check of what arbi-core actually has installed. 10 findings. The owner
   said "Fix everything": 9 are fixed in this repo, and `PK-7` closes when
   0.1.1 is published and Project_A moves to it.

**Purpose:** one place to see four things:

- how clean, efficient and tested every package and file is
- which passes are done
- what was found and fixed
- what is still open

The rules being checked against are in `Standards_and_Tracker.md`.

---

## How a pass works

A **pass** reviews one package, one file at a time, in the order its section
lists:

1. **Read and list.** I read the file in full, against the checklist below,
   score it, and list its findings by type, each with an ID. Every
   recommendation says what it changes for a consumer. Non-trivial fixes come
   with a before/after. The file's row becomes `in review`.
2. **Decide.** The owner approves which findings get fixed. Nothing is written
   before that.
3. **Fix and verify.** I apply the approved fixes, then run `uv run pytest -q`
   and `uv run pyrefly check` from the repository root. Both must stay green
   (baseline: **38 passed**, **0 errors**). A behavior fix lands with a test
   that fails without it. A change to parsing is also checked against
   arbi-core's real inputs (Standards §4).
4. **Re-score.** I re-rate the file and mark it `closed`, then move to the next
   file.
5. **Close.** After the last file, I review the package as a whole (structure,
   exports, duplication, layering, ownership), close the pass row, refresh its
   LOC, and the owner commits.

A finding that belongs to another file goes into the ledger with that file's
ID and waits for that file's pass. It isn't fixed early.

### The file checklist

| Check | Looks for |
|---|---|
| **Correctness** | Bugs and unhandled edge cases (year boundaries, leap days, single-digit parts, letter case, locale). Typed errors instead of bare `KeyError`/`TypeError`/`ValueError`. |
| **Date rules** | The year boundary, next-weekday and Today/Tomorrow rules hold, and the clock is read only through `datetime.now()`, once per conversion (Standards §1.5). |
| **Truthful docs** | Docstrings, Args, Returns and Raises that match the code. Examples that say which "today" they assume. Docstrings follow Standards §1.3. |
| **Dead code** | Unused imports, parameters, functions, error classes or constants; branches that can never run. |
| **Consistency** | Standards §1.4: short sentences joined with periods (no em dashes), module docstring, trailing newline, `X \| None` typing, keyword arguments at call sites, American spelling, `_` prefixes only with a stated reason, `__all__` matching imports, banners. |
| **Layering and ownership** | Imports point down only (Standards §2.7); every concern stays with its one owner (Standards §2.6). |
| **Simplicity** | Duplication, overlong functions, deep nesting, magic values that belong in `constants`. |
| **Efficiency** | Repeated work per call that could be done once (regex compiling, table building, log messages built and thrown away). |
| **Tests** | The file's behavior is pinned by an offline test on the frozen clock. |

**Pass 6 (tests) checks instead:**
- each test pins behavior a consumer depends on; tests that only restate
  the obvious are removed and listed;
- tests are offline and deterministic, and every date is written against the
  frozen clock;
- names and docstrings say what is being pinned.

**Pass 7 (docs) checks instead:** every claim matches the code at the
current commit; examples run; IDs, versions and counts are current; each doc
sticks to what it owns (Standards header table).

### Scores

| Score | Clean | Eff |
|---|---|---|
| 9–10 | Truthful docs, consistent style and typing, no dead code, clear names | No repeated work per call |
| 7–8 | Minor nits: spacing, comment fluff, stale wording | Small repeated work, tolerable |
| ≤6 | Docs that are wrong, dead checks, bad names, structural duplication, real bugs | Real waste |

**Tests:** ✓ behavior covered · partial · none · n/a (nothing to test).
**Status:** `closed` = reviewed, fixed, re-rated · `in review` · `pending`.

**Finding IDs:** `KN-` kernel · `CV-` conversions · `PS-` parsers · `PK-`
package root and packaging · `TS-` tests · `DOC-` README and docs. New IDs
continue each prefix's numbering.

---

## Round 1 passes

Passes ran bottom-up through the layering, so each file was reviewed after
everything it imports.

| # | Pass | Files | LOC | Clean | Eff | Open findings | Status |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | `kernel` | 5 | 467 | 9 | 10 | 0 | **closed** 2026-10-26 (final pass: `KN-15`, `KN-17` fixed) |
| 2 | `conversions`: clock and name | 2 | 106 | 10 | 10 | 0 | **closed** 2026-10-26 (final pass: `CV-12` fixed) |
| 3 | `parsers` | 6 | 356 | 10 | 10 | 0 | **closed** 2026-10-26 (final pass: `PS-12` fixed) |
| 4 | `conversions`: `convert_datetime` and `__init__` | 2 | 72 | 10 | 10 | 0 | **closed** 2026-10-26 (final pass: `CV-10`, `CV-11` fixed) |
| 5 | Package root (`__init__.py`, `pyproject.toml`, `py.typed`, `.python-version`) | 4 | 112 | 10 | 10 | 0 | **closed** 2026-10-26 (`PK-5` fixed; `PK-7` is outside this repo) |
| 6 | `tests/` | 7 | 716 | 10 |  | 0 | **closed** 2026-10-26 (final pass: `TS-3` fixed) |
| 7 | README + `docs/` | 6 |  | 10 |  | 0 | **closed** 2026-10-26 (final pass: `DOC-9`, `DOC-10` fixed) |
|  | **Total** | **32** | | | | **0** in this repo | 7 of 7 closed |

LOC counted 2026-10-26, after the fixes (Python files and `pyproject.toml`).
A pass score is the lowest file score in it. Scores are as of the final pass.

---

## File-level detail

### 1. kernel: closed

| File | Clean | Eff | Tests | Notes |
|---|---:|---:|---|---|
| `constants.py` | 9 | 10 | ✓ | Patterns built from each name's own spellings; any case; 1–2 digit days and months; any year; whitespace between parts (`KN-4` to `KN-7`, `KN-11` to `KN-14`). `TEST_CASES` moved to the tests (`KN-3`). Was 4. |
| `errors.py` | 9 | 10 | ✓ | `ConviError` (alias `LabError`), `InvalidReferenceError`; three reserved errors documented (`KN-10`, `KN-2`). Was 7. |
| `logging_config.py` | 9 | 10 | ✓ | One package logger, built once (`KN-1`). Was 6. |
| `utils.py` | 10 | 10 | ✓ | Removes every kind of whitespace (`KN-5`). Was 7. |
| `__init__.py` | 10 | 10 | n/a | |

### 2. conversions: clock and name: closed

| File | Clean | Eff | Tests | Notes |
|---|---:|---:|---|---|
| `convert_clock_format.py` | 9 | 10 | ✓ | 12-hour arithmetic, locale-free (`CV-7`); `from err` (`CV-3`); no log-and-raise (`CV-8`). `CV-9` kept. Was 6. |
| `convert_name.py` | 10 | 10 | ✓ | Any iterable, typed errors (`CV-2`); opt-in `score_cutoff` (`CV-1`); no log-and-raise (`CV-8`). Was 6. |

### 3. parsers: closed

| File | Clean | Eff | Tests | Notes |
|---|---:|---:|---|---|
| `parser_handler.py` | 10 | 10 | ✓ | `resolve_date()` owns the year boundary rule: a given year kept, the next occurrence otherwise, Feb 29 included (`PS-1`, `PS-2`); one `today` per conversion (`PS-9`). Was 4. |
| `parse_datetime.py` | 9 | 10 | ✓ | Numbers parsed directly; `today=`; lazy log calls (`PS-4`, `PS-6`, `PS-11`). Was 6. |
| `parse_day_month_time.py` | 10 | 10 | ✓ | Month number from `MONTHS`, locale-free (`PS-8`); dead check gone (`PS-3`). Was 5. |
| `parse_day_time.py` | 10 | 10 | ✓ | `next_weekday()`, `relative_day()` (`PS-7`); dead guards gone (`PS-3`). Was 7. |
| `process_patterns.py` | 10 | 10 | ✓ | `PATTERN_HANDLERS`, pinned equal to `TIME_PATTERNS` (`PS-5`); reads the clock once. Was 8. |
| `__init__.py` | 10 | 10 | n/a | |

### 4. conversions: `convert_datetime` and `__init__`: closed

| File | Clean | Eff | Tests | Notes |
|---|---:|---:|---|---|
| `convert_datetime.py` | 10 | 10 | ✓ | Trims instead of deleting spaces; `PatternMatchError`'s message (`CV-5`); `except Exception` kept (`CV-4`, intentional). Was 8. |
| `__init__.py` | 10 | 10 | n/a | |

### 5. Package root: closed

| File | Clean | Eff | Tests | Notes |
|---|---:|---:|---|---|
| `convi_lab/__init__.py` | 10 | 10 | ✓ | One list of the public API, in `__all__` (`PK-6`). |
| `pyproject.toml` | 10 | n/a | ✓ | Python 3.10, 3.13, 3.14 and `rapidfuzz` 3.0.0 checked. |
| `.idea/` | | | n/a | `PK-5`: untracked 2026-10-26 (staged, not committed). |

### 6. tests: closed

| File | Tests | Notes |
|---|---:|---|
| `conftest.py` | n/a | Frozen clock, and a `clock` fixture for other days or a ticking clock (`TS-2`). |
| `test_convert_datetime.py` | 15 | Every format; arbi-core's scraped shape; the date rules; Feb 29; New Year's Eve; any case, short forms, whitespace, digits, years. |
| `test_parsers.py` | 5 | Routing, `today=`, the two tables, typed errors. |
| `test_conversions.py` | 8 | Clock (with a German locale), names, cutoff, references. |
| `test_errors.py` | 2 | Hierarchy, messages. |
| `test_logging.py` | 3 | One handler, one line per failure, no log-and-raise. |
| `test_package.py` | 4 | Public names, version, clean import, layering. |

37 tests. Each bug fix landed with tests that failed before it (listed per
step below).

### 7. README + docs: closed

| File | Clean | Notes |
|---|---:|---|
| `README.md` | 10 | Rewritten (`DOC-1`, `DOC-2`, `DOC-6`, `DOC-7`, `DOC-8`). All 4 code blocks run on their own with warnings as errors; 15 commented results and 16 format-table claims checked on the frozen clock. |
| `docs/*.md` | 10 | Updated to the code at the end of round 1. |

---

## arbi-core compatibility

arbi-core (Project_A `packages/core`) is convi-lab's main consumer. It calls
`convert_date_time()` on the first 10 characters of each scraped row (always
`dd/mmHH:MM`, like `"27/1019:30"`) and `convert_name()` for team names, with a
cache. It ships with convi-lab **0.1.0**. Nothing in Project_A was changed:
the new code was put first on the path with `PYTHONPATH`, and `git status`
there was the same before and after.

| Check | Inputs | 0.1.0 | Round 1 code |
|---|---|---|---|
| Logged scraped dates (`[:10]`), on 3 clocks | 99 distinct, plus all 1,487 raw lines | 99/99 converted | **0 differences**, after every step |
| Team names against every league's team list | 195 names × 10 leagues = 1,950 | baseline | **0 differences**, after every step |
| arbi-core's own `parse_raw_event_data` → `populate_league_games` → `build_event`, on every logged page | 17 pages × 10 leagues | 2,520 events, 0 dropped | **identical events** (teams and dates) |
| arbi-core's test suite | 307 tests | 305 passed, 2 failed | **305 passed, the same 2 failed** |

The 2 failures are `test_score_league_matchups_uses_all_four_checks` (its
`PASS`/`FAIL` cases). They fail with 0.1.0 too, and don't touch convi-lab.

Also checked: 7,884 generated inputs (every shape, spaced and compact, years,
names, AM/PM) on 3 clocks against 0.1.0. After step 1, 0 differed. After
step 2, 4,509 differed, and every one is intended: 4,392 are `PS-1` (a given
year kept) and 117 are `PS-2` (Feb 29 → the next leap year). The new 12-hour
arithmetic matches the old `strptime("%I:%M%p")` on all 768 hour, minute and
AM/PM combinations.

---

## Findings ledger (Round 1)

### Open

| ID | Sev | Where | Finding | Closes when |
|---|---|---|---|---|
| `PK-7` | **risk** | Project_A's venv (not this repo) | **arbi-core runs a hand-patched convi-lab 0.1.0.** The published 0.1.0 fails to import with logger-lab 0.2.0 (`ModuleNotFoundError: logger_lab.main`, checked with `uv --no-cache`), and Project_A pins logger-lab 0.2.0. The installed copy works because `logging_config.py` was added and 7 files edited on Oct 24 (hashes don't match `RECORD`). The files are hardlinked to uv's cache, so the edit also altered the cached 0.1.0, which now fails on `convi_lab.logging_config`. Any reinstall breaks arbi-core at import. | 0.1.1 is published, and Project_A pins `convi-lab>=0.1.1,<0.2`, runs `uv cache clean convi-lab` and `uv sync` (`Continuation.md` §3, Phase 3). Nothing in this repo is left to do. |

### Fixed in the final pass (2026-10-26)

The final pass (owner: "do one final cleanliness pass") re-read every file,
scanned every file for the §1.4 house style, probed edge cases (pandas and
numpy values, a string reference, year `0000`, 50,000-character inputs:
linear, 23 ms), and checked what arbi-core has installed. Owner: "Fix
everything". Verified after the fixes: `pytest` 38 passed on Python 3.10, 3.13
and 3.14; `pyrefly` 0 errors; the house-style scan clean; the README check; the
arbi-core checks (below the table).

Not findings: the error classes' `__init__`s have no docstring of their own
(they only build the message their class docstring documents); the `print`
in `ConviError`'s docstring example; the em dash inside Standards §1.4's
verbatim baseline rule.

| ID | Sev | Was | Fix | Test that failed before |
|---|---|---|---|---|
| `CV-10` | **bug** | `convert_date_time(pd.NA)` raised `TypeError` (truth tested before the type), breaking "never raises"; `Series.map(convert_date_time)` crashed on a missing value. `InvalidInputError(pd.NA)` failed the same way. | The type is checked first, in both. A blank string now says "got a blank string". | `test_missing_values_return_empty_string` (reproduced with real `pandas.NA` too) |
| `CV-12` | risk | `convert_name("Mon", "Monday")` matched letters and returned `"M"`. | A `str` reference raises `InvalidReferenceError`. | `test_name_with_a_reference_that_is_not_iterable_raises_typed` |
| `DOC-9` | **bug** | `Continuation.md` said 0.1.0 logged through `investigator` to a file (that's the git history, not what arbi-core runs). | Corrected, with `PK-7`. | n/a |
| `KN-15` | nit | Out-of-date docstrings in `errors.py` (`DateComponentError`, `ClockFormatError`, `FuzzyMatchError`, `PatternMatchError`) and `utils.py`. | Rewritten to the code. | n/a |
| `KN-17` | nit | Two lines over 120 characters in `constants.py`; `SEP` without `_RE`. | Wrapped (with `DATE_RE`, `OPTIONAL_YEAR_RE`); `SEP_RE`. The compiled patterns are byte-for-byte unchanged (checked). | n/a |
| `CV-11` | nit | A third copy of the formats table in `convert_date_time`'s docstring; `if resolved:`; mixed quotes. | Points to the API Reference; `is not None`; `""` throughout. | n/a |
| `PS-12` | nit | A 130-character docstring line; `PATTERN_HANDLERS` typed `Callable`; comment fluff. | Wrapped; `Callable[..., datetime]` (called with `today=`); loop tidied. | n/a |
| `TS-3` | nit | Stale `test_parsers` docstring; a literal NBSP in a test; 2 long lines; 2 helpers without docstrings; positional `convert_name` calls. | All fixed. The NBSP is written `"\u00a0"`. | n/a |
| `DOC-10` | nit | The README's `convert_name` examples were positional. | Keyword arguments. | README check: 15 results, 0 mismatches |
| `PK-5` | nit | IDE settings were tracked in git. | `git rm -r --cached .idea` (owner). Staged; local files kept; `.gitignore` covers them. | n/a |

### Fixed in round 1 (2026-10-26)

Each step ran `uv run pytest -q` and `uv run pyrefly check` (both green), and
the arbi-core comparison.

| Step | ID | Sev | Was | Fix | Test that failed before |
|---|---|---|---|---|---|
| 1 | `KN-6` | bug | Years outside 2025–2029 didn't parse. | Any 2- or 4-digit year. | `test_any_year_with_two_or_four_digits` |
| 1 | `KN-7` | bug | One-digit days and months failed. | 1–2 digits, two tried first. Whitespace kept as an optional separator, so `"1/1 11:00"` and `"1/11 1:00"` stay apart. | `test_single_digit_day_and_month` |
| 1 | `KN-5` | bug | Tabs and NBSP inside the input failed. | `\s*` between parts; `remove_spaces()` removes all whitespace. | `test_any_whitespace_between_parts` |
| 1 | `KN-11` | bug | Day and month names were case-sensitive. | `re.IGNORECASE`. | `test_names_in_any_case` |
| 1 | `KN-12` | bug | `Tues`, `Thurs`, `Weds`, `Sept` were rejected. | Each name's own spellings (`DAY_SHORT_FORMS`, `MONTH_SHORT_FORMS`). | `test_common_abbreviations` |
| 1 | `KN-13` | risk | Made-up names (`"Decuary"`) resolved to a wrong date. | Same as `KN-12`. | `test_made_up_names_are_rejected` |
| 1 | `KN-14`, `KN-4` | nit | Duplicate day regex; `_` and lowercase constant names. | One `DAY_NUMBER_RE`; plain upper-case names. | n/a |
| 1 | `PS-4`, `PS-6` | nit | Double separator replace; stale docstring examples. | Parsed once; examples say which "today" they assume. | n/a |
| 2 | `PS-1` | bug | A given year was thrown away (`"12.04.2025"` → 2027). | `resolve_date()`: a given year is exact (D-6). | `test_a_given_year_is_kept` |
| 2 | `PS-2` | bug | Feb 29 raised a bare `ValueError` or returned `""`. | Without a year, the next real Feb 29 (D-7). | `test_february_29_is_the_next_real_one` |
| 2 | `PS-9` | bug | The clock was read several times; New Year's Eve gave a year off. | One `datetime.now()` per conversion; `today=` on the parsers. | `test_the_clock_is_read_once_per_conversion`, `test_parsers_take_an_explicit_today` |
| 2 | `PS-3` | nit | Dead checks in the parsers. | Removed with the rewrite. | n/a |
| 2 | `PS-8` | bug | `%B` made month names depend on the locale. | Month number from `MONTHS`. | `test_results_do_not_depend_on_the_locale` |
| 3 | `CV-7` | bug | `%p` made AM/PM depend on the locale. | 12-hour arithmetic. | `test_results_do_not_depend_on_the_locale` |
| 3 | `CV-3` | nit | No `from err`. | Added. | n/a |
| 4 | `CV-2` | bug | A bad reference raised a bare `TypeError`. | Validated once; `InvalidReferenceError`; one-pass iterables read into a list. | `test_name_with_a_reference_that_is_not_iterable_raises_typed`, `test_name_reference_of_any_iterable` |
| 4 | `PS-5` | risk | Two tables shared their keys by hand. | `PATTERN_HANDLERS`, pinned equal to `TIME_PATTERNS`. | `test_every_pattern_has_exactly_one_parser` |
| 4 | `CV-5` | nit | The no-match warning rebuilt a message by hand. | `PatternMatchError`'s message. | n/a |
| 4 | `KN-2` | risk | Three errors are never raised. | Kept and documented as reserved (removing them would break `except` clauses). | n/a |
| 5 | `KN-1` | risk | Seven console handlers built at import; the app couldn't control them. | One logger-lab logger, `convi_lab`; module loggers propagate to it (D-5). | `test_one_package_logger_holds_the_only_handler` |
| 5 | `CV-8` | risk | Errors were logged where raised; one failure printed twice. | Only the boundary logs. | `test_a_failure_is_logged_once_at_the_boundary`, `test_raising_code_logs_nothing` |
| 5 | `PS-11` | nit | f-strings in log calls were built on every parse. | Lazy `%s` arguments. | n/a |
| 6 | `KN-10` | risk | `LabError` shared logger-lab's name. | `ConviError`; `LabError` kept as an alias. | `test_hierarchy` |
| 6 | `CV-1` | risk | No score cutoff. | Opt-in `score_cutoff`, off by default (arbi-core unchanged). | `test_name_cutoff_is_opt_in` |
| 6 | `KN-3` | nit | `TEST_CASES` exported as public API. | Moved to the tests as `SAMPLES`. | n/a |
| 6 | `PS-7` | nit | `_` prefixes without a reason. | `next_weekday`, `relative_day`, `PATTERN_HANDLERS`, plain locals. | n/a |
| 7 | `PS-10`, `PK-6` | nit | Comments repeating docstrings; the API listed twice. | Removed; `__all__` is the one list. | n/a |
| 7 | `DOC-1`, `DOC-6` | bug | README results were wrong, and its error example never errored. | Rewritten and run. | README check: 15 results, 0 mismatches |
| 7 | `DOC-7`, `DOC-2`, `DOC-8` | nit | The README's `convert_name` claim was untrue; roadmap in the README; style. | Rewritten; roadmap in `Continuation.md`. | n/a |
| 7 | `TS-2` | nit | One fixed day only. | `clock` fixture: other days, a ticking clock. | n/a |

### Fixed before round 1 (2026-10-26, no behavior change)

| ID | Was | Fix |
|---|---|---|
| `PK-1` | `pyproject.toml` had no `[build-system]`, so uv treated convi-lab as a virtual project and `import convi_lab` failed in its own venv. A stale `egg-info` hid it. | `uv_build` backend; `uv sync` installs it editable. |
| `PK-2` | No license, authors, URLs, classifiers, `py.typed` or `__version__`. | Added, in logger-lab's shape. `__version__` reads the package metadata. |
| `PK-3` | logger-lab 0.1.1 API (`with_profile("INVESTIGATOR")` per module, one `from logger_lab.main import lab`). | logger-lab `>=0.2.0,<0.3`; one `build_logger()` in the kernel. |
| `PK-4` | Untracked `egg-info` and `__pycache__` folders; no `.gitignore`. | Removed; root `.gitignore` from logger-lab's. |
| `KN-8` | The kernel imported upward: `pattern_parsers` imported `parsers`, `utils.parser_handler` lazily imported the package root, and every module imported `convi_lab.logging_config` from the root. | `conversion_kernel` → `kernel` (owner). `logging_config` moved into it. `process_patterns` and `parser_handler` moved into `parsers`. Pinned by `test_imports_point_down_the_layers`, shown to fail on an upward import. |
| `KN-9` | `DayResolutionError` and `MonthResolutionError` kept their own copies of the day and month names. | They use `DAYS` and `MONTHS`. Messages unchanged (pinned). |
| `TS-1` | No `tests/`. Each module had a `test_case()` / `__main__` block that printed or logged its output, plus `match_pattern` and `_test_pattern` helpers in the kernel. | A `tests/` suite on a frozen clock (owner). The blocks and the two helpers are gone. |
| `CV-6` | `reference: iter` is not a type (pyrefly: 2 errors). | A real type. pyrefly: 0 errors. |
| `DOC-3` | Untruthful docstrings (`convert_name` "returns `""`", `remove_spaces` "all whitespace", and others). | Corrected. |
| `DOC-4` | House style: em dashes, British spelling, `Optional[...]`, missing module docstrings, positional multi-argument calls, broken comments. | Fixed across `src/`. |
| `DOC-5` | README: `logger-lab >= 0.1.1`, `convi_lab.conversion_kernel.utils`. | Updated. |

---

## Intentional (do not "fix")

| What | Why |
|---|---|
| `convert_date_time()` returns `""` instead of raising, and catches `Exception` (`CV-4`) | It's the safe boundary (Standards §2.1). arbi-core's scraping loop relies on it. It logs unexpected errors with their traceback. |
| `PatternMatchError`, `DayResolutionError`, `MonthResolutionError` are never raised (`KN-2`) | Reserved in 0.1.x: removing exported names would break `except` clauses. Revisit in 0.2.0. |
| `convert_to_24_format()` returns a `datetime` on 1900-01-01 (`CV-9`) | A `time` return is an API change. Revisit in 0.2.0. |
| `convert_name()` has no cutoff by default | Changing the default would change arbi-core's team matching. The cutoff is opt-in. |
| Compact input reads two-digit numbers first (`"1/111:00"` is November 1, 01:00) | It matches 0.1.0 for every compact input 0.1.0 accepted. Spaced input (`"1/1 11:00"`) is never ambiguous. |
| A weekday that is today means next week | "Tuesday 12:30" on a Tuesday is read as an upcoming event. |
| `"Today 09:00"` at 10:00 returns today 09:00, in the past | "Today" names the date explicitly. Only dates without a year move forward. |
| `conversions` and `parsers` import each other as packages | Their modules form a strict order (Standards §2.7). Only the package `__init__`s gather both. |

---

## Updating this doc

- A new finding gets the next ID of its prefix, a severity, and a
  recommendation that says what it changes.
- A fixed finding moves to a "Fixed" table with the date and how it was
  verified.
- A pass row's LOC, scores and open count are refreshed when the pass closes.
