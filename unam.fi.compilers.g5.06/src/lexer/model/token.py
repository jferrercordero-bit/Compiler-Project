"""Un token reconocido: tipo, lexema y posición donde empieza."""

from dataclasses import dataclass

from .token_type import TokenClass, TokenType


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    @property
    def token_class(self) -> TokenClass:
        return self.type.token_class
