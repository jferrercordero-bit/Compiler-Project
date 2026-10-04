"""Lexical error handler."""

from dataclasses import dataclass

STRING_STATES = {"q5", "q20"}
CHAR_STATES = {"q21", "q22", "q23"}
COMMENT_STATES = {"q10", "q11"}


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
        """Returns the position where scanning should resume."""
        end_of_line = text.find("\n", pos)
        if end_of_line == -1:
            end_of_line = len(text)
        if stuck_state in STRING_STATES:
            return end_of_line  # Skip to the end of the line to avoid interpreting the remaining characters as separate tokens.
        if stuck_state in CHAR_STATES:
            closing = text.find("'", pos + 1, end_of_line)
            return closing + 1 if closing != -1 else end_of_line
        if stuck_state in COMMENT_STATES:
            return len(text)
        return pos + 1  # Skip the unexpected character and continue scanning.
