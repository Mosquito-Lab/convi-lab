"""
The kernel: the base layer. It holds the constants, errors, logging and string helpers.

Nothing here imports from the rest of convi_lab.
"""

from .logging_config import build_logger
from .utils import remove_spaces

__all__ = [
    'build_logger',
    'remove_spaces',
]
