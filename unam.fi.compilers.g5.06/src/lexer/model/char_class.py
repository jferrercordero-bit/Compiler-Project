"""Las 18 clases de caracteres: las columnas de la tabla de transiciones (sección 5.3)."""

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
    """Devuelve la columna de la tabla para el carácter c.

    Se usan rangos explícitos y no str.isalpha(), porque isalpha() también
    acepta letras con acento, que en este lenguaje no forman identificadores.
    """
    if "a" <= c <= "z" or "A" <= c <= "Z" or c == "_":
        return "L"
    if "0" <= c <= "9":
        return "D"
    return _SINGLE.get(c, "OTHER")
