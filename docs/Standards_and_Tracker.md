# Standards and tracker

**Documentation snapshot: 2026-10-26**

This document defines how convi-lab is changed. Every module, function and doc
is held to it.

| Doc | Owns |
|---|---|
| `Standards_and_Tracker.md` (this file) | The rules, plus the high-level workstream tracker |
| `Cleanliness_Tracker.md` | The file-by-file review ledger: scores, finding IDs, decisions, fixes |
| `Continuation.md` | Status, roadmap, the changes per version and open design decisions |
| `API_Reference.md` | The public API, the supported formats and the date rules |
| `Framework_Comparison.md` | Where convi-lab stands against other date-parsing libraries |

Status and task order live **only** in `Continuation.md`. Findings live **only**
in `Cleanliness_Tracker.md`. Neither is repeated here.

---

## 1. Baseline standard (shared by every project)

> **Baseline.** Section 1 is copied word for word into every project's standards
> doc (logger-lab, LabFrame, Project A, …). A project may **add** rules under
> §1.5 for its own special cases, but it never removes or rewords a baseline
> rule. To change the baseline, change it in every project in the same pass.

### 1.1 Collaboration

1. **Break work into steps and take one problem at a time.** List what needs
   doing, let the owner choose the order, and do not run everything at once.
2. **Show the proposed change before writing it**, unless the owner has
   explicitly approved that change. An approval covers that change only, not
   the next one.
3. **Findings are listed, not silently fixed.** A problem found while doing
   something else is recorded with an ID, and the owner decides what happens
   to it.
4. **Check the real source.** Describe what the code does now, read from the
   file itself and its callers. Do not rely on a previous doc's description of
   it, or on what a name implies.
5. **Use git only when the owner asks.** Preserve the owner's unrelated local
   changes.
6. **Docs:** the trackers (the cleanliness ledger and the continuation/status
   doc) are updated in the same turn as the approved work they record. Every
   other doc changes only when the owner asks.
7. **Report honestly.** After each step, say what was verified and how, what
   was not verified, and what remains. "Not run" stays "not run".

### 1.2 Code

1. **Prefer simple code.** Use plain functions, lists, dicts and loops unless
   an abstraction solves a real problem that exists now.
2. **One owner per concern.** Every responsibility lives in exactly one place
   (each project lists its owners in §2).
3. **Validate once, at the boundary.** Check inputs where they enter. Code
   further in trusts what it was given.
4. **Fail loudly and with types.** Predictable failures raise the project's own
   exception types, with a message that says what to do. Never `print()` an
   error. Never let a predictable failure surface as a bare `KeyError` or
   `TypeError`.
5. **Use keyword arguments** when a call has more than one meaningful argument.
6. **Names describe intent.** They should be clear first, and a little fun
   where it fits naturally (`get_stylish()`, `conspiracy_theorist`).
   Clear-and-plain beats clever-but-vague.
7. **Optimize measured costs.** A shorter loop is not automatically an
   improvement. Optimize the paths that actually run often or cost I/O.
8. **No side effects on import**, beyond deliberate registration.
9. **Imports point down a declared layering** (each project defines it in §2).

### 1.3 Docstrings

Every function and class gets a docstring. That includes internal helpers, and
any `__init__` that does real work. In order, wherever they apply, it answers:

1. **What does the library do here automatically?**
2. **What must the caller supply?** For an extension point, give the exact
   signature to implement.
3. **How is it used?** A short `Example::`.

```python
def function(arg: Type) -> ReturnType:
    """
    One-line summary.

    One or two sentences: why it exists and which side of the
    library/consumer line it sits on.

    Note: anything surprising or easy to misuse.

    Args:
        arg: ...
    Returns:
        ...
    Raises:
        `SomeError`: when ...
    Example::
        function(value)
    """
```

- The docstring matches the code: Args, Returns and Raises are complete and
  use current names.
- Keep it short. If something needs a paragraph to explain, the code can
  usually be clearer.
- An extension point's docstring **is** its implementation guide. Someone
  should be able to write a correct implementation from the docstring alone.

### 1.4 House style

- Every file starts with a module docstring and ends with one blank line.
- Type hints use `X | None`, not `Optional[X]` or `Union[...]`.
- Use American spelling (`normalize`, `color`, `serialize`).
- **Don't use a `_` prefix by default.** Only mark something private for a real
  reason, and say why in a short comment. Real reasons are a name collision, a
  safety invariant, or wiring that is implementation only.
- Anything public from a package is listed in its `__all__`. Anything imported
  into an `__init__` is either exported there or not imported at all.
- Use section banners (`# Lookup helpers #` boxes) to split longer modules.
- **Comments use plain `#`**, never `#:` doc-comments. A constant's comment
  goes on the same line as the constant:
  `DEFAULT_FILENAME = "app.log"  # Log file name inside the log directory`.
  There is no `Final` on module constants; the module docstring says what they
  are for.
- **Write short, plain sentences.** Join thoughts with a period, not an em
  dash (—) or a double hyphen (`--`). Split a sentence once it runs past about
  25 words. PyCharm flags long ones. This holds for docstrings, comments,
  error messages, docs and chat.

### 1.5 convi-lab additions to the baseline

- **The clock is read in one way only:** `datetime.now()`, through a
  module-level `from datetime import datetime`. The tests freeze that name
  in every module, so a date rule that reads the clock any other way
  (`date.today()`, `time.time()`) escapes the frozen clock and makes the
  suite depend on the day it runs.
- **The clock is read once per conversion.** `process_patterns()` reads
  `datetime.now()` once and passes it down as `today=`. Two reads can
  straddle midnight and disagree on the date.
- **Results are relative to today.** A doc or example that shows a resolved
  date says which "today" it assumes.
- **Results never depend on the locale.** No `strptime` directive that reads
  names (`%B`, `%b`, `%A`, `%a`, `%p`). Names and AM/PM are resolved by the
  library itself.
- **arbi-core is the main consumer.** A change to parsing is checked against
  arbi-core's real inputs before it ships (§4).

---

## 2. Core development standard (convi-lab)

1. **One safe boundary.** `convert_date_time()` is the entry point for
   consumers. It never raises: every failure is logged and returns `""`.
   Everything below it (`process_patterns()`, the parsers, `convert_name()`,
   `convert_to_24_format()`) raises the typed errors of §3.2 and lets them
   through.
2. **Whitespace between parts is optional.** Every pattern in
   `TIME_PATTERNS` allows any whitespace (`\s*`) between the parts, so spaced
   and compact input both match. `convert_date_time()` only trims the ends.
   Spaces are never deleted before matching: that would make `"1/1 11:00"`
   and `"1/11 1:00"` the same string. Names match in any case.
3. **One pattern, one parser.** Each entry of `TIME_PATTERNS` has exactly one
   parser, and each parser reads exactly one pattern's groups.
4. **Every parser ends in `parser_handler()`.** It resolves the date with
   `resolve_date()`, which owns the year boundary rule, then joins it with
   the time. A given year is exact. Without one, the date is its next
   occurrence on or after today.
5. **Fuzzy matching goes through `convert_name()`.** Day and month names are
   resolved with it, never with a local lookup.
6. **One owner per concern:**

   | Concern | Owner |
   |---|---|
   | Day and month names and their short forms, regex fragments, `TIME_PATTERNS` | `kernel.constants` |
   | The error hierarchy and every error message | `kernel.errors` |
   | The package logger (`convi_lab`, the only handler) | `kernel.logging_config.PACKAGE_LOGGER` |
   | Each module's logger (a child, no handler) | `kernel.logging_config.build_logger()` |
   | Removing whitespace from a captured part | `kernel.utils.remove_spaces()` |
   | Reading a time as 12- or 24-hour | `conversions.convert_clock_format.convert_to_24_format()` |
   | Fuzzy name matching | `conversions.convert_name.convert_name()` |
   | One parser per pattern | `parsers.parse_datetime`, `parsers.parse_day_time`, `parsers.parse_day_month_time` |
   | The year boundary rule | `parsers.parser_handler.resolve_date()` |
   | Joining date and time | `parsers.parser_handler.parser_handler()` |
   | The pattern-to-parser table | `parsers.process_patterns.PATTERN_HANDLERS` |
   | Choosing the parser for an input; the one clock read | `parsers.process_patterns.process_patterns()` |
   | The safe boundary, the output format, and logging a failure | `conversions.convert_datetime.convert_date_time()` |
   | Checking the import layering | `tests/test_package.py` |

7. **Layering: imports point down only.**

   ```text
   kernel: constants ← errors ← logging_config, utils        (base)
       ← conversions.convert_clock_format, conversions.convert_name
       ← parsers: parse_* ← parser_handler, process_patterns
       ← conversions.convert_datetime
       ← convi_lab/__init__.py
   ```

   Nothing in a lower layer imports a higher one, at module level or inside
   a function. `tests/test_package.py` checks every module against this
   order. Package `__init__` files only gather exports, so the check skips
   them, except the kernel's.

   Note: the *modules* form a strict order, but the `conversions` and
   `parsers` *packages* import each other. This works because the top-level
   `__init__.py` always loads `conversions` first. Keep that import first.
8. **Validate once, at the boundary.** `convert_date_time()` checks the input
   type and emptiness, and `convert_name()` its reference. The parsers trust
   the regex match they are given.
9. **Log once, at the boundary.** Code that raises doesn't log.
   `convert_date_time()` logs each failure it turns into `""`, once.
10. **Docs match behavior**, and that includes the README.

---

## 3. Public API standard

### 3.1 Adding an input format

| Step | Where |
|---|---|
| A compiled pattern, named, with `\s*` between parts and `re.IGNORECASE` | `kernel.constants.TIME_PATTERNS` |
| A parser `(match, today=None)` that reads its groups and ends in `parser_handler()` | a new `parsers/parse_*.py` |
| Its entry in the pattern-to-parser table | `parsers.process_patterns.PATTERN_HANDLERS` |
| An export, if it's public | `parsers/__init__.py` and `convi_lab/__init__.py` |
| Tests: the format spaced and compact, its errors | `tests/test_convert_datetime.py`, `tests/test_parsers.py` |
| The arbi-core check: its real inputs give the same results (§4) | before release |
| A row in the formats table | `API_Reference.md` and the README |

### 3.2 Errors

- Every error the library raises is a `ConviError` subclass (`LabError` is its
  old name, kept as an alias), and each one sits
  in the hierarchy documented in `errors.py` and the API Reference.
- An error message names the bad value and how to fix it (for example, it
  lists the valid names).
- A wrapped low-level error is raised with `from err`.
- A new failure mode gets a new subclass under the right branch: parser or
  conversion.

### 3.3 Public surface

- `convi_lab/__init__.py`'s `__all__` lists exactly what consumers import
  from the top level.
- Subpackage `__init__`s export their own layer's tools (`convi_lab.kernel`,
  `convi_lab.conversions`, `convi_lab.parsers`).
- A removal or rename of anything public is listed in `Continuation.md` with
  the version it changed in.

---

## 4. Verification standard

From the repository root:

```bash
uv run pytest -q
```

```bash
uv run pyrefly check
```

- **Setup:** the `uv_build` backend means `uv sync` installs `convi_lab` as
  editable. `pytest` and `pyrefly` are in the `dev` dependency group. Tests
  live in `tests/` and the pyrefly config is in `pyproject.toml`.
- **Tests run offline on a frozen clock.** `tests/conftest.py` freezes
  `datetime.now()` at Wednesday 2026-05-13 10:00 in every `convi_lab` module,
  for every test. Expected dates are written against that day. The `clock`
  fixture sets another day, or a clock that ticks (New Year's Eve).
- **What must be pinned:**
  - every supported format, spaced and compact, with and without AM/PM, in
    any case, with every short form;
  - arbi-core's scraped shape (`"27/1019:30"`);
  - the date rules: a given year, the year boundary, Feb 29, the next
    weekday, Today and Tomorrow, one clock read per conversion;
  - a non-English locale;
  - the `""` boundary for bad types, blanks, unmatched and unparseable input;
  - `process_patterns()`: routing, `None` on no match, typed errors through;
  - the clock and name conversions, and their errors;
  - every error message and the hierarchy;
  - logging: one handler, one line per failure, no log-and-raise;
  - the public surface, `__version__`, a warning-free import, and the layering.
- **arbi-core check, before a release.** Run arbi-core's real inputs through
  the working tree and compare with the convi-lab it ships with: the dates and
  team names from its bot logs, its own `populate_league_games()` on every
  logged page, and its test suite. Put the working tree first on the path
  with `PYTHONPATH=<convi-lab>/src`, so nothing in Project_A changes. Every
  difference must be an intended one.
- **Tests are few and pointed.** One test per behavior, with edge cases as their
  own cases. A list of members or values is looped inside one test, not
  parametrized into dozens. A bug fix lands with a test shown to fail without
  the fix.
- **Recorded baseline (2026-10-26, Windows, after the final pass):** `pytest`
  **38 passed** on Python 3.10, 3.13 and 3.14. The suite also passed against
  `rapidfuzz` 3.0.0, the lowest version `pyproject.toml` allows (checked at 18
  tests, before round 1). `pyrefly` reports **0 errors and 4 suppressed**, from
  three `pyrefly: ignore` comments on deliberate wrong-type calls in tests. The
  layering test was shown to fail on an upward import. arbi-core: 0
  differences on its logged inputs, identical scraped events, and its suite
  unchanged (305 passed, the same 2 unrelated failures).

---

## 5. High-level tracker

| Workstream | Status | Current note |
|---|---|---|
| logger-lab 0.2.0 migration | Done 2026-10-26 | Pinned `>=0.2.0,<0.3`; every module builds its logger with `kernel.logging_config.build_logger()` |
| Packaging for 0.1.1 | Done 2026-10-26 | `uv_build`, metadata, `dev` group, `py.typed`, `__version__` |
| `conversion_kernel` → `kernel` | Done 2026-10-26 | The kernel is the base layer, pinned by the layering test |
| Test and type-check baseline | Done 2026-10-26 | 38 passed · pyrefly clean · frozen clock with a `clock` fixture |
| Behavior-neutral fixes (pre-pass) | Done 2026-10-26 | Imports, typing, truthful docstrings, house style (`Cleanliness_Tracker.md`) |
| Docs (`docs/`) | Done 2026-10-26 | Standards, Continuation, API Reference, Cleanliness Tracker, Framework Comparison |
| Cleanliness passes, round 1 | Done 2026-10-26 | All 7 passes closed; 13 bugs fixed, each with a failing test first; 1 open (`PK-5`, git) |
| arbi-core compatibility | Done 2026-10-26 | 0 differences on its real inputs; identical scraped events; its suite unchanged |
| Final cleanliness pass | Done 2026-10-26 | 10 findings: 9 fixed here; `PK-7` (arbi-core's hand-patched install) closes when 0.1.1 is published and pinned |
| Publish 0.1.1 | Pending | The owner commits, then says when to publish |

---

## 6. Immediate priority

Commit and push (on the owner's word), publish 0.1.1, then move arbi-core's
pin (`Continuation.md` §5).
