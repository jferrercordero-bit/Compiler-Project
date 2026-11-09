"""Errores léxicos y su recuperación en modo pánico (sección 5.4)."""

from dataclasses import dataclass

STRING_STATES = frozenset({"q5", "q20"})
CHAR_STATES = frozenset({"q21", "q22", "q23"})
COMMENT_STATES = frozenset({"q10", "q11"})


@dataclass(frozen=True)
class LexicalError:
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"Lexical error {self.line}:{self.column}: {self.message}"


class ErrorHandler:
    def __init__(self) -> None:
        self.errors: list[LexicalError] = []

    @staticmethod
    def message_for(stuck_state: str, char: str) -> str:
        if stuck_state in STRING_STATES:
            return "unterminated string literal"
        if stuck_state in CHAR_STATES:
            return "malformed character constant"
        if stuck_state in COMMENT_STATES:
            return "unterminated comment"
        return f"unexpected character '{char}'"

    def report(self, line: int, column: int, stuck_state: str, char: str) -> None:
        self.errors.append(LexicalError(line, column, self.message_for(stuck_state, char)))

    @staticmethod
    def recover(text: str, pos: int, stuck_state: str) -> int:
        """Devuelve la posición donde se reanuda el escaneo."""
        end_of_line = text.find("\n", pos)
        if end_of_line == -1:
            end_of_line = len(text)
        if stuck_state in STRING_STATES:
            return end_of_line  # el salto de línea se escanea después como espacio
        if stuck_state in CHAR_STATES:
            # Hasta la siguiente comilla simple de la misma línea, para que 'ab'
            # no se convierta en un identificador falso más otro error.
            closing = text.find("'", pos + 1, end_of_line)
            return closing + 1 if closing != -1 else end_of_line
        if stuck_state in COMMENT_STATES:
            return len(text)
        return pos + 1  # carácter inesperado: se salta solo ese carácter
