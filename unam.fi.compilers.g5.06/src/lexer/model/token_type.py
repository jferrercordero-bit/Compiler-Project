"""Definition of the token types and their classes. The classes are used to group the types in the output."""

from enum import Enum


class TokenClass(Enum):
    """The 7 classes seen during class. The value is the label that is printed."""

    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    CONSTANT = "constant"
    LITERAL = "literal"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    SPECIAL = "special"

    @property
    def label(self) -> str:
        """Label in lowercase, for the line with the sequence of tokens."""
        return self.value

    @property
    def title(self) -> str:
        """Label with initial uppercase, for the lines 'Class: lexeme'."""
        return self.value.capitalize()


_K = TokenClass.KEYWORD
_I = TokenClass.IDENTIFIER
_C = TokenClass.CONSTANT
_L = TokenClass.LITERAL
_O = TokenClass.OPERATOR
_P = TokenClass.PUNCTUATION
_S = TokenClass.SPECIAL


class TokenType(Enum):
    """Each type keeps its number in the catalog and its class."""

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
