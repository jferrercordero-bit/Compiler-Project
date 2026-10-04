"""Lexical scanner implementation."""

from .char_class import char_class
from .error_handler import COMMENT_STATES, ErrorHandler
from .symbol_table import SymbolTable
from .token import Token
from .token_classifier import TokenClassifier
from .token_type import TokenType
from .transition_table import START, TransitionTable


def _advance(text: str, start: int, end: int, line: int, column: int) -> tuple[int, int]:
    """Update line and column numbers after consuming text[start:end]."""
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
        # "is None" and not "or": an empty SymbolTable is false due to its __len__ method.
        self.table = TransitionTable() if table is None else table
        self.errors = ErrorHandler() if errors is None else errors
        self.symbols = SymbolTable() if symbols is None else symbols
        self.classifier = TokenClassifier() if classifier is None else classifier

    def scan(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        pos, line, column = 0, 1, 1
        n = len(text)
        while pos < n:
            # Go through the DFA keeping the last final state visited.
            state, i = START, pos
            last_final, last_end = None, pos
            while i < n:
                nxt = self.table.next_state(state, char_class(text[i]))
                if nxt is None:
                    break
                state, i = nxt, i + 1
                if self.table.is_final(state):
                    last_final, last_end = state, i

            # Rule 4: the input ended inside an unterminated block comment.
            if i == n and state in COMMENT_STATES:
                self.errors.report(line, column, state, text[pos])
                break

            # Rule 5: there is no valid token if no final state was reached.
            if last_final is None:
                self.errors.report(line, column, state, text[pos])
                resume = self.errors.recover(text, pos, state)
                line, column = _advance(text, pos, resume, line, column)
                pos = resume
                continue

            # Extract the lexeme up to the last final state.
            lexeme = text[pos:last_end]
            kind = self.classifier.classify(last_final, lexeme)
            if kind is not None:  # Skip whitespace and comments.
                tokens.append(Token(kind, lexeme, line, column))
                if kind is TokenType.ID:
                    self.symbols.record(lexeme, line)
            line, column = _advance(text, pos, last_end, line, column)
            pos = last_end
        return tokens
