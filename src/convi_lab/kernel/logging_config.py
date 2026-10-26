"""
logging_config.py: the one place convi-lab's loggers are built.

The package logger (``convi_lab``) is built once, here, with logger-lab: a
console output at WARNING. Every module logger is its child, with no handler
of its own, so each record is handled once. An app changes what convi-lab
prints through that one logger::

    logging.getLogger("convi_lab").setLevel(logging.ERROR)   # quieter
"""

import logging

from logger_lab import lab

PACKAGE_LOGGER_NAME = "convi_lab"  # The parent of every module logger, and the only one with a handler

# Built at import: the package's one deliberate registration (Standards §1.2.8)
PACKAGE_LOGGER = lab().with_output("CONSOLE").with_level("WARNING").build(PACKAGE_LOGGER_NAME)


def build_logger(name: str) -> logging.Logger:
    """
    Return the logger for one convi-lab module.

    Every module calls this once, at import, with its ``__name__``. The logger
    has no handler of its own: its records go up to ``convi_lab``, and its
    level comes from there.

    Args:
        name: The module's ``__name__`` (``convi_lab.…``).
    Returns:
        The module's ``logging.Logger``.
    Example::
        logger = build_logger(__name__)
    """

    return logging.getLogger(name)
