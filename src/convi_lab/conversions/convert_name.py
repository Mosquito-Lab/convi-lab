"""
convert_name.py: fuzzy name matching against a reference list, with rapidfuzz.
"""

from collections.abc import Collection, Iterable

from rapidfuzz import process, utils

from convi_lab.kernel.errors import FuzzyMatchError, InvalidReferenceError


def convert_name(name: str, reference: Iterable[str], score_cutoff: float | None = None) -> str:
    """
    Return the closest match for *name* within *reference* using fuzzy matching.

    Uses rapidfuzz's ``extractOne()`` with its default scorer (WRatio) and the
    built-in ``default_process`` preprocessor (lowercases, strips punctuation).

    Note: by default there is no score cutoff. A non-empty *reference* always
    returns its best entry, even when nothing in it is close. Pass
    *score_cutoff* to make a poor match raise instead.

    Args:
        name: Input string to match (e.g. ``"Mon"``, ``"A. Hawks"``).
        reference: The canonical strings to match against, in any iterable
            (e.g. a list of day names or team names, a generator).
        score_cutoff: The lowest score (0 to 100) that counts as a match, or
            ``None`` for no cutoff.
    Returns:
        The best-matching string from *reference*.
    Raises:
        `InvalidReferenceError`: when *reference* is a single string, or can't be iterated.
        `FuzzyMatchError`: when *reference* is empty, nothing reaches *score_cutoff*, or rapidfuzz raises.
    Example::
        convert_name(name="Mon", reference=DAYS)     # "Monday"
        convert_name(name="Jul", reference=MONTHS)   # "July"
        convert_name(name="Nets", reference=TEAMS)   # "Brooklyn Nets"
        convert_name(name="zzz", reference=DAYS, score_cutoff=80)   # raises FuzzyMatchError
    """

    # Validate once. A string is one name, not a list of names (iterating it would match letters)
    if isinstance(reference, str) or not isinstance(reference, Iterable):
        raise InvalidReferenceError(reference)

    # A one-pass iterable (a generator) is read into a list, so it can be counted
    choices: Collection[str] = reference if isinstance(reference, Collection) else list(reference)

    try:
        result = process.extractOne(name, choices, processor=utils.default_process, score_cutoff=score_cutoff)

    except Exception as e:
        raise FuzzyMatchError(name=name, ref_count=len(choices)) from e

    if result is None:
        raise FuzzyMatchError(name=name, ref_count=len(choices))

    match, _score, _idx = result  # Only the match is used; the score and index are not
    return match
