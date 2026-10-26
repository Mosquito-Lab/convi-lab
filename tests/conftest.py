"""
Shared test setup: every test runs on a frozen clock.

The parsers resolve "Today", weekdays and the year boundary from
``datetime.now()``. Freezing it makes every expected date fixed, whatever day
the suite runs on. A test that needs another day (or a clock that ticks over
midnight) sets it with the ``clock`` fixture.
"""

import sys
from datetime import datetime

import pytest

import convi_lab  # noqa: F401  # Loads every module, so the clock below reaches all of them

NOW = datetime(2026, 5, 13, 10, 0)  # The default frozen "now": a Wednesday morning


class FrozenDatetime(datetime):
    """
    A ``datetime`` whose ``now()`` returns the frozen moments in turn.

    Each call returns the next of ``moments``, and the last one repeats. The
    default is ``NOW`` forever. Everything else (``strptime``, ``combine``,
    arithmetic) is the real ``datetime``.
    """

    moments = [NOW]  # Set per test through the ``clock`` fixture

    @classmethod
    def now(cls, tz=None):
        """Return the next frozen moment, ignoring the real clock."""

        moment = cls.moments.pop(0) if len(cls.moments) > 1 else cls.moments[0]
        return cls.combine(moment.date(), moment.time(), tzinfo=tz)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    """
    Freeze the clock in every convi_lab module that imported ``datetime``.

    The modules use ``from datetime import datetime``, so each module's own
    ``datetime`` name is swapped for ``FrozenDatetime``.
    """

    monkeypatch.setattr(FrozenDatetime, "moments", [NOW])
    for name, module in list(sys.modules.items()):
        if name.startswith("convi_lab") and getattr(module, "datetime", None) is datetime:
            monkeypatch.setattr(module, "datetime", FrozenDatetime)


@pytest.fixture
def clock(monkeypatch):
    """
    Set the frozen clock for one test.

    Call it with one moment to freeze there, or several for a clock that
    ticks: each ``now()`` returns the next one.

    Example::
        def test_new_year(clock):
            clock(datetime(2026, 12, 31, 23, 59, 59), datetime(2027, 1, 1))
    """

    def set_clock(*moments: datetime) -> None:
        """Make ``now()`` return *moments* in turn, then the last one forever."""

        monkeypatch.setattr(FrozenDatetime, "moments", list(moments))

    return set_clock
