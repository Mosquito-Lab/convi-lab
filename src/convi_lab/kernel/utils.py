"""
utils.py: small string helpers. The parsers use them on the parts a pattern captured.
"""


def remove_spaces(value: str) -> str:
    """
    Remove every whitespace character from *value*.

    Spaces, tabs, newlines and non-breaking spaces all go. The parsers use it
    to clean the parts a pattern captured (``"10 : 15"`` → ``"10:15"``).

    Args:
        value: The string to clean.
    Returns:
        *value* without whitespace.
    Example::
        remove_spaces("17 Jul -\t02:00 PM")   # "17Jul-02:00PM"
    """

    return "".join(value.split())
