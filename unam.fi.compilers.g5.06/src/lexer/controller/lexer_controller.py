"""Ejecuta las etapas en orden: preprocesar, escanear y reunir tokens, errores y símbolos."""

from dataclasses import dataclass

from ..model.error_handler import ErrorHandler, LexicalError
from ..model.preprocessor import Preprocessor
from ..model.scanner import Scanner
from ..model.symbol_table import SymbolTable
from ..model.token import Token
from ..model.transition_table import TransitionTable


@dataclass
class LexResult:
    tokens: list[Token]
    errors: list[LexicalError]
    symbols: SymbolTable


class LexerController:
    def __init__(self, table: TransitionTable | None = None) -> None:
        # La tabla se carga una sola vez y se reutiliza en cada ejecución.
        self.table = TransitionTable() if table is None else table
        self.preprocessor = Preprocessor()

    def run(self, text: str) -> LexResult:
        errors, symbols = ErrorHandler(), SymbolTable()
        scanner = Scanner(self.table, errors, symbols)
        tokens = scanner.scan(self.preprocessor.normalize(text))
        return LexResult(tokens, errors.errors, symbols)
