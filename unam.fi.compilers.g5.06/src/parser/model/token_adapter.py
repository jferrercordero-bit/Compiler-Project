"""Convert lexer tokens into parser input symbols."""

from dataclasses import dataclass

from lexer.model.token import Token
from lexer.model.token_type import TokenType

# Map these token types to fixed symbols regardless of their lexemes..
_BY_TYPE = {
    TokenType.ID: "id",
    TokenType.INT_CONST: "num",
    TokenType.FLOAT_CONST: "real",
    TokenType.CHAR_CONST: "chr",
    TokenType.STRING: "str",
}


@dataclass(frozen=True)
class InputSymbol:
    """A parser input symbol with its original lexeme, line, and column."""

    terminal: str
    lexeme: str
    line: int
    column: int

    def shown(self) -> str:
        return "end of input" if self.terminal == "$" else f"'{self.lexeme}'"


def adapt(tokens: list[Token]) -> list[InputSymbol]:
    """Map selected token types to fixed symbols and use the lexeme otherwise.
    STRING maps to 'str', which is outside the current grammar. Other
    unsupported tokens, such as 'return' and '==', keep their lexemes.
    """
    return [
        InputSymbol(_BY_TYPE.get(t.type, t.lexeme), t.lexeme, t.line, t.column)
        for t in tokens
    ]
