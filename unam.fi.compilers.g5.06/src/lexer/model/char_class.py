"""Defines the 18 character classes used as columns in the DFA transition table."""

CLASSES = (
    "L", "D", "DOT", "QUOTE", "APOS", "BSLASH", "SLASH", "STAR", "EQ",
    "REL", "AMP", "BAR", "ARITH", "PUNCT", "HASH", "WS", "NL", "OTHER",
)

_SINGLE = {
    ".": "DOT",
    '"': "QUOTE",
    "'": "APOS",
    "\\": "BSLASH",
    "/": "SLASH",
    "*": "STAR",
    "=": "EQ",
    "!": "REL", "<": "REL", ">": "REL",
    "&": "AMP",
    "|": "BAR",
    "+": "ARITH", "-": "ARITH", "%": "ARITH",
    "(": "PUNCT", ")": "PUNCT", "{": "PUNCT", "}": "PUNCT",
    "[": "PUNCT", "]": "PUNCT", ";": "PUNCT", ",": "PUNCT",
    "#": "HASH",
    " ": "WS", "\t": "WS", "\r": "WS",
    "\n": "NL",
}


def char_class(c: str) -> str:
    """Returns the transition-table class for character c.

    Explicit ranges are used instead of str.isalpha() because isalpha()
    also accepts accented letters, which are not valid in identifiers
    for this language.
    """
    if "a" <= c <= "z" or "A" <= c <= "Z" or c == "_":
        return "L"
    if "0" <= c <= "9":
        return "D"
    return _SINGLE.get(c, "OTHER")
