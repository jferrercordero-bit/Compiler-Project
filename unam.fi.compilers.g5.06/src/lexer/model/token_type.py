"""Catálogo de los 45 tipos de token (sección 2 del Entregable del Model Designer)."""

from enum import Enum


class TokenClass(Enum):
    """Las 7 clases vistas en clase. El valor es la etiqueta que se imprime."""

    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    CONSTANT = "constant"
    LITERAL = "literal"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    SPECIAL = "special"

    @property
    def label(self) -> str:
        """Etiqueta en minúsculas, para la línea con la secuencia de tokens."""
        return self.value

    @property
    def title(self) -> str:
        """Etiqueta con mayúscula inicial, para las líneas 'Class: lexeme'."""
        return self.value.capitalize()


_K = TokenClass.KEYWORD
_I = TokenClass.IDENTIFIER
_C = TokenClass.CONSTANT
_L = TokenClass.LITERAL
_O = TokenClass.OPERATOR
_P = TokenClass.PUNCTUATION
_S = TokenClass.SPECIAL


class TokenType(Enum):
    """Cada tipo guarda su número en el catálogo y su clase."""

    INT = (1, _K)
    FLOAT = (2, _K)
    CHAR = (3, _K)
    DOUBLE = (4, _K)
    VOID = (5, _K)
    RETURN = (6, _K)
    IF = (7, _K)
    ELSE = (8, _K)
    WHILE = (9, _K)
    FOR = (10, _K)
    PRINT = (11, _K)
    ID = (12, _I)
    INT_CONST = (13, _C)
    FLOAT_CONST = (14, _C)
    CHAR_CONST = (15, _C)
    TRUE = (16, _C)
    FALSE = (17, _C)
    STRING = (18, _L)
    PLUS = (19, _O)
    MINUS = (20, _O)
    STAR = (21, _O)
    SLASH = (22, _O)
    PERCENT = (23, _O)
    ASSIGN = (24, _O)
    EQ = (25, _O)
    NOT = (26, _O)
    NEQ = (27, _O)
    LT = (28, _O)
    LE = (29, _O)
    GT = (30, _O)
    GE = (31, _O)
    AMP = (32, _O)
    AND = (33, _O)
    BAR = (34, _O)
    OR = (35, _O)
    LPAREN = (36, _P)
    RPAREN = (37, _P)
    LBRACE = (38, _P)
    RBRACE = (39, _P)
    LBRACKET = (40, _P)
    RBRACKET = (41, _P)
    SEMI = (42, _P)
    COMMA = (43, _P)
    HASH = (44, _S)
    DOT = (45, _S)

    def __init__(self, number: int, token_class: TokenClass) -> None:
        self.number = number
        self.token_class = token_class
