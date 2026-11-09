"""Run lexical analysis, LL(1) parsing, and semantic analysis in order."""

from dataclasses import dataclass, field

from lexer.controller.lexer_controller import LexerController
from lexer.model.error_handler import LexicalError
from lexer.model.symbol_table import SymbolTable

from ..model.grammar import Grammar
from ..model.ll1_parser import LL1Parser, ParseError, TraceRow
from ..model.ll1_table import LL1Table
from ..model.parse_tree import Node
from ..model.sdt import SDTError, SDTEvaluator
from ..model.token_adapter import InputSymbol, adapt


@dataclass
class ParseResult:
    input: list[InputSymbol]
    symbols: SymbolTable
    lexical_errors: list[LexicalError] = field(default_factory=list)
    syntax_error: ParseError | None = None
    sdt_errors: list[SDTError] = field(default_factory=list)
    tree: Node | None = None
    trace: list[TraceRow] = field(default_factory=list)
    sdt_completed: bool = False

    @property
    def parsing_ok(self) -> bool:
        return (
            self.tree is not None
            and not self.lexical_errors
            and self.syntax_error is None
        )

    @property
    def sdt_ok(self) -> bool:
        # Require a completed semantic analysis with no reported errors.
        return self.parsing_ok and self.sdt_completed and not self.sdt_errors


class ParserController:
    def __init__(self) -> None:
        # Build the grammar and parsing table once per controller instance.
        # LL1Table raises LL1Conflict if two productions need the same cell.
        self.grammar = Grammar.load()
        self.table = LL1Table(self.grammar)
        self.parser = LL1Parser(self.table)
        self.lexer = LexerController()

    def run(self, text: str, trace: bool = False) -> ParseResult:
        lexed = self.lexer.run(text)
        result = ParseResult(adapt(lexed.tokens), lexed.symbols)
        if lexed.errors:
            # Skip parsing and semantic analysis if the lexer reports errors.
            result.lexical_errors = lexed.errors
            return result
        try:
            result.sdt_completed = True
            result.tree = self.parser.parse(result.input, result.trace if trace else None)
        except ParseError as error:
            result.syntax_error = error
            return result
        result.sdt_errors = SDTEvaluator(lexed.symbols).evaluate(result.tree)
        return result
