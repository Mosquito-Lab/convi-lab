"""
convert_name.py — Fuzzy name matching against a reference list via rapidfuzz.
"""

from logger_lab import lab
from rapidfuzz import process, utils

from convi_lab.conversion_kernel.errors import FuzzyMatchError

logger = (
    lab()
    .with_profile("INVESTIGATOR")
    .with_level("ERROR")
    .build(__name__)
)

# Function to match fuzzy names
def convert_name(name: str, reference: iter) -> str:
    """
    Return the closest match for *name* within *reference* using fuzzy matching.

    Uses rapidfuzz's ``extractOne()`` with its default scorer (WRatio) and the
    built-in ``default_process`` pre-processor (lowercases, strips punctuation).

    Examples:
        convert_name("Mon",  DAYS)     # → "Monday"
        convert_name("Jul",  MONTHS)   # → "July"
        convert_name("Nets", TEAMS)    # → "Brooklyn Nets"
    Args:
        name: Input string to match (e.g. ``"Mon"``, ``"A. Hawks"``).
        reference: List of canonical strings to match against
                      (e.g. full day names, team names).
    Returns:
        The best-matching string from *reference*, or ``""`` on failure.
    """

    try:
        result = process.extractOne(name, reference, processor=utils.default_process)

    except Exception as e:
        logger.error(f"rapidfuzz raised for {name!r}: {e}", exc_info=True)
        raise FuzzyMatchError(name, len(reference)) from e

    if result is None:
        logger.error(f"No fuzzy match for {name!r} in {len(reference)}-item reference")
        raise FuzzyMatchError(name, len(reference))

    match, _score, _idx = result
    return match


# Example usage and test case
def test_case():
    """Input a name and list to return best match"""

    _list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
             "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets"]

    _inputs = ['Mon', 'Nets', 'A. Hawks', 'Fri']

    for _input in _inputs:
        logger.debug(f"input: {_input}, output: {convert_name(_input, _list)}")


if __name__ == "__main__":
    # TEST
    test_case()