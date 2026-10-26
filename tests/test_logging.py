"""
How convi-lab logs: one package logger with the only handler, and one line per failure.
"""

import logging
import sys

import pytest

from convi_lab import FuzzyMatchError, ClockFormatError, convert_date_time, convert_name, process_patterns


class Collect(logging.Handler):
    """A handler that keeps every record it gets."""

    def __init__(self) -> None:
        """Start with no records."""

        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep *record*."""

        self.records.append(record)


@pytest.fixture
def records():
    """Every record that reaches the ``convi_lab`` package logger during the test."""

    collect = Collect()
    package = logging.getLogger("convi_lab")
    package.addHandler(collect)
    yield collect.records
    package.removeHandler(collect)


def test_one_package_logger_holds_the_only_handler():
    """``convi_lab`` has one handler at WARNING. Every module logger has none and passes records up (KN-1)."""

    package = logging.getLogger("convi_lab")
    # pytest adds its capture handlers to every non-propagating logger, so count only logger-lab's
    ours = [handler for handler in package.handlers if type(handler).__module__.startswith("logger_lab")]
    assert len(ours) == 1
    assert package.level == logging.WARNING

    module_loggers = [
        module.logger for name, module in sys.modules.items()
        if name.startswith("convi_lab.") and isinstance(getattr(module, "logger", None), logging.Logger)
    ]
    assert module_loggers
    for logger in module_loggers:
        assert logger.handlers == [], logger.name
        assert logger.propagate, logger.name
        assert logger.getEffectiveLevel() == logging.WARNING, logger.name


def test_a_failure_is_logged_once_at_the_boundary(records):
    """``convert_date_time`` logs one line per failure. Code that raises doesn't log (CV-8)."""

    assert convert_date_time("Today 13:00 PM") == ""
    assert [record.levelname for record in records] == ["ERROR"]

    records.clear()
    assert convert_date_time("garbage") == ""
    assert [record.levelname for record in records] == ["WARNING"]


def test_raising_code_logs_nothing(records):
    """A caller that handles the typed error itself sees nothing printed (CV-8)."""

    with pytest.raises(ClockFormatError):
        process_patterns("Today 13:00 PM")
    with pytest.raises(FuzzyMatchError):
        convert_name(name="Mon", reference=[])
    assert records == []
