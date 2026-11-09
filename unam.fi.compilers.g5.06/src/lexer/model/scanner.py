"""Ciclo de escaneo por máximo bocado (secciones 3 y 6.2 del Model Designer)."""

from .char_class import char_class
from .error_handler import COMMENT_STATES, ErrorHandler
from .symbol_table import SymbolTable
from .token import Token
from .token_classifier import TokenClassifier
from .token_type import TokenType
from .transition_table import START, TransitionTable


def _advance(text: str, start: int, end: int, line: int, column: int) -> tuple[int, int]:
    """Actualiza línea y columna con los caracteres consumidos, incluidos los descartados."""
    for ch in text[start:end]:
        if ch == "\n":
            line, column = line + 1, 1
        else:
            column += 1
    return line, column


class Scanner:
    def __init__(
        self,
        table: TransitionTable | None = None,
        errors: ErrorHandler | None = None,
        symbols: SymbolTable | None = None,
        classifier: TokenClassifier | None = None,
    ) -> None:
        # "is None" y no "or": una SymbolTable vacía es falsa por su __len__.
        self.table = TransitionTable() if table is None else table
        self.errors = ErrorHandler() if errors is None else errors
        self.symbols = SymbolTable() if symbols is None else symbols
        self.classifier = TokenClassifier() if classifier is None else classifier

    def scan(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        pos, line, column = 0, 1, 1
        n = len(text)
        while pos < n:
            # Recorrer el AFD guardando el último estado final visitado (regla 1).
            state, i = START, pos
            last_final, last_end = None, pos
            while i < n:
                nxt = self.table.next_state(state, char_class(text[i]))
                if nxt is None:
                    break
                state, i = nxt, i + 1
                if self.table.is_final(state):
                    last_final, last_end = state, i

            # Regla 4: la entrada se acabó dentro de un comentario de bloque.
            # No se retrocede al "/" de q8; se reporta y se deja de escanear.
            if i == n and state in COMMENT_STATES:
                self.errors.report(line, column, state, text[pos])
                break

            # Regla 5: sin estado final no hay token.
            if last_final is None:
                self.errors.report(line, column, state, text[pos])
                resume = self.errors.recover(text, pos, state)
                line, column = _advance(text, pos, resume, line, column)
                pos = resume
                continue

            # Cortar el lexema en el último estado final (retroceso).
            lexeme = text[pos:last_end]
            kind = self.classifier.classify(last_final, lexeme)
            if kind is not None:  # espacios y comentarios se descartan (regla 3)
                tokens.append(Token(kind, lexeme, line, column))
                if kind is TokenType.ID:
                    self.symbols.record(lexeme, line)
            line, column = _advance(text, pos, last_end, line, column)
            pos = last_end
        return tokens
