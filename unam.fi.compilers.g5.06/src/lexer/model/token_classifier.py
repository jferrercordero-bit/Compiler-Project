"""Asigna el TokenType según el estado final y el lexema (secciones 2 y 5.3)."""

from .token_type import TokenType as T

# Tabla de búsqueda: se consulta solo para lexemas que terminan en q1.
LOOKUP = {
    "int": T.INT, "float": T.FLOAT, "char": T.CHAR, "double": T.DOUBLE,
    "void": T.VOID, "return": T.RETURN, "if": T.IF, "else": T.ELSE,
    "while": T.WHILE, "for": T.FOR, "print": T.PRINT,
    "true": T.TRUE, "false": T.FALSE,
}

OPERATORS = {
    "+": T.PLUS, "-": T.MINUS, "*": T.STAR, "/": T.SLASH, "%": T.PERCENT,
    "=": T.ASSIGN, "==": T.EQ, "!": T.NOT, "!=": T.NEQ,
    "<": T.LT, "<=": T.LE, ">": T.GT, ">=": T.GE,
    "&": T.AMP, "&&": T.AND, "|": T.BAR, "||": T.OR,
}

PUNCTUATION = {
    "(": T.LPAREN, ")": T.RPAREN, "{": T.LBRACE, "}": T.RBRACE,
    "[": T.LBRACKET, "]": T.RBRACKET, ";": T.SEMI, ",": T.COMMA,
}

SPECIALS = {"#": T.HASH, ".": T.DOT}

# Estados finales cuyo lexema se reconoce pero no es token (regla 3 de prioridad).
DISCARDED_STATES = frozenset({"q9", "q18", "q19"})

_OPERATOR_STATES = frozenset({"q7", "q8", "q12", "q13", "q14", "q15"})
_FIXED = {"q2": T.INT_CONST, "q4": T.FLOAT_CONST, "q24": T.CHAR_CONST, "q6": T.STRING}


class TokenClassifier:
    def classify(self, final_state: str, lexeme: str) -> T | None:
        """Devuelve el TokenType, o None si el lexema se descarta."""
        if final_state in DISCARDED_STATES:
            return None
        if final_state == "q1":
            # Regla 2 de prioridad: la tabla gana sobre identificador.
            return LOOKUP.get(lexeme, T.ID)
        if final_state in _FIXED:
            return _FIXED[final_state]
        if final_state in _OPERATOR_STATES:
            return OPERATORS[lexeme]
        if final_state == "q16":
            return PUNCTUATION[lexeme]
        if final_state == "q17":
            return SPECIALS[lexeme]
        raise ValueError(f"{final_state} no es un estado final")
