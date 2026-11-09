"""Non-recursive Predictive LL(1) Parser: that uses a stack, an input buffer, and the parsing table M[A, a]."""

from dataclasses import dataclass

from .grammar import END, EPSILON
from .ll1_table import LL1Table
from .parse_tree import Node
from .token_adapter import InputSymbol


class ParseError(Exception):
    def __init__(self, line: int, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.message = message


@dataclass(frozen=True)
class TraceRow:
    step: int
    stack: str    	# The bottom of the stack is on the left and the top is on the right.
    input: str
    action: str


def _quote_list(symbols: list[str]) -> str:
    quoted = [f"'{s}'" if s != END else "end of input" for s in symbols]
    if len(quoted) == 1:
        return quoted[0]
    if len(quoted) == 2:
        return f"{quoted[0]} or {quoted[1]}"
    return "one of " + ", ".join(quoted[:-1]) + f" or {quoted[-1]}"


class LL1Parser:
    TRACE_INPUT_TOKENS = 12

    def __init__(self, table: LL1Table) -> None:
        self.table = table
        self.grammar = table.grammar

    def parse(self, symbols: list[InputSymbol], trace: list[TraceRow] | None = None) -> Node:
        last_line = symbols[-1].line if symbols else 1
        buffer = [*symbols, InputSymbol(END, END, last_line, 0)]
        root = Node(self.grammar.start)
        stack: list[Node] = [Node(END), root]
        pos, step = 0, 0
        previous: InputSymbol | None = None

        while True:
            top, look = stack[-1], buffer[pos]
            step += 1

            def log(action: str) -> None:
                if trace is not None:
                    trace.append(TraceRow(step, self._stack_text(stack),
                                          self._input_text(buffer, pos), action))

            if top.symbol == END:
                if look.terminal == END:
                    log("accept")
                    return root
                error = self._error([END], look, previous)
                log(f"error: {error.message}")
                raise error

            if not self.grammar.is_nonterminal(top.symbol):
                if top.symbol == look.terminal:
                    log(f"match {look.terminal}")
                    top.token = look
                    stack.pop()
                    previous, pos = look, pos + 1
                    continue
                error = self._error([top.symbol], look, previous)
                log(f"error: {error.message}")
                raise error

            production = self.table.get(top.symbol, look.terminal)
            if production is None:
                error = self._error(self.table.expected(top.symbol), look, previous)
                log(f"error: {error.message}")
                raise error
            log(str(production))
            stack.pop()
            top.production = production
            top.children = [Node(s) for s in production.body] or [Node(EPSILON)]
            for child in reversed(top.children):
                if child.symbol != EPSILON:
                    stack.append(child)

    def _error(self, expected: list[str], look: InputSymbol,
               previous: InputSymbol | None) -> ParseError:
        # Report a missing semicolon only when the stack confirms that ';'
        # is the next required terminal and the input has reached a boundary.
        if previous is not None and ";" in expected and (
                look.terminal == END or look.line > previous.line):
            return ParseError(previous.line, f"missing ';' after '{previous.lexeme}'")
        if look.terminal == END:
            line = previous.line if previous else 1
            return ParseError(line, f"unexpected end of input, expected {_quote_list(expected)}")
        return ParseError(look.line, f"unexpected {look.shown()}, expected {_quote_list(expected)}")

    @staticmethod
    def _stack_text(stack: list[Node]) -> str:
        return " ".join(node.symbol for node in stack)

    def _input_text(self, buffer: list[InputSymbol], pos: int) -> str:
        rest = [s.terminal for s in buffer[pos:]]
        if len(rest) > self.TRACE_INPUT_TOKENS + 1:
            rest = rest[:self.TRACE_INPUT_TOKENS] + ["…", END]
        return " ".join(rest)
