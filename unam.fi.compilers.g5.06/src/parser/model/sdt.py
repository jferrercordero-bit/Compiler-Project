"""Evaluate the semantic rules on a completed parse tree.

The attribute rules are L-attributed. A left-to-right, depth-first
traversal evaluates them in dependency order. Inherited attributes
are passed as arguments, and synthesized attributes are returned.
"""

from dataclasses import dataclass

from lexer.model.symbol_table import SymbolTable

from .parse_tree import Node
from .type_system import (CONSTANT_TYPE, ERROR, WIDTH, arithmetic, assignable,
                          negate)

UNDECLARED = "TBD"   # Placeholder type assigned by the lexer to identifiers in the symbol table.


@dataclass(frozen=True)
class SDTError:
    line: int
    message: str


class SDTEvaluator:
    def __init__(self, symbols: SymbolTable) -> None:
        self.symbols = symbols
        self.errors: list[SDTError] = []
        self.offset = 0          # Next available relative address.
        self.declared_in: dict[str, int] = {}

    def evaluate(self, root: Node) -> list[SDTError]:
        self._program(root)
        return self.errors

    def _error(self, line: int, message: str) -> None:
        self.errors.append(SDTError(line, message))

    # (1) Program → Stmt StmtList
    def _program(self, node: Node) -> None:
        stmt, rest = node.children
        self._stmt(stmt)
        self._stmt_list(rest)

    # (2) StmtList → Stmt StmtList   (3) StmtList → ε
    def _stmt_list(self, node: Node) -> None:
        while node.production.number == 2:
            stmt, node = node.children
            self._stmt(stmt)

    # (4) Stmt → Decl   (5) Stmt → Assign
    def _stmt(self, node: Node) -> None:
        child = node.children[0]
        if node.production.number == 4:
            self._decl(child)
        else:
            self._assign(child)

    # (6) Decl → Type id Decl'
    # Pass Type.type as Decl'.inh. Check the initializer before registering a new declaration.
    def _decl(self, node: Node) -> None:
        type_node, id_node, rest = node.children
        declared_type = self._type(type_node)
        rest.attrs["inh"] = declared_type
        self._decl_rest(rest, declared_type, id_node.token.lexeme)

        name, line = id_node.token.lexeme, id_node.token.line
        entry = self.symbols.lookup(name) or self.symbols.insert(name, line)
        if entry.type != UNDECLARED:
            first = self.declared_in.get(name, entry.lines[0] if entry.lines else line)
            self._error(line, f"'{name}' is already declared in line {first}")
            return
        entry.type = declared_type
        entry.size = WIDTH[declared_type]
        entry.dimension = 0
        entry.address = self.offset
        self.offset += WIDTH[declared_type]
        self.declared_in[name] = line
        id_node.attrs["address"] = entry.address

    # (7) Decl' → ;                  There is no initializer to check.
    # (8) Decl' → = Expr ;  Check assignable(Decl'.inh, Expr.type) if Expr.type is not ERROR.
    def _decl_rest(self, node: Node, declared_type: str, name: str) -> None:
        if node.production.number == 7:
            return
        _, expr, _ = node.children
        value_type = self._expr(expr)
        if value_type != ERROR and not assignable(declared_type, value_type):
            self._error(node.children[0].token.line,
                        f"type mismatch: '{name}' is {declared_type} but the value is {value_type}")

    # (9) Assign → id = Expr ;  Check the target declaration and evaluate Expr.
    def _assign(self, node: Node) -> None:
        id_node, eq, expr, _ = node.children
        name = id_node.token.lexeme
        entry = self.symbols.lookup(name)
        target = entry.type if entry and entry.type != UNDECLARED else None
        if target is None:
            self._error(id_node.token.line, f"'{name}' is not declared")
        else:
            id_node.attrs["type"] = target
        value_type = self._expr(expr)
        if target is not None and value_type != ERROR and not assignable(target, value_type):
            self._error(eq.token.line,
                        f"type mismatch: '{name}' is {target} but the value is {value_type}")

    # (10) Type → int   (11) Type → float   (12) Type → char
    #      Type.type := int | float | char;  Type.width := 4 | 4 | 1
    def _type(self, node: Node) -> str:
        type_name = node.children[0].symbol
        node.attrs["type"] = type_name
        node.attrs["width"] = WIDTH[type_name]
        return type_name

    # (13) Expr → Term Expr'         Expr'.inh := Term.type;  Expr.type := Expr'.syn
    def _expr(self, node: Node) -> str:
        term, rest = node.children
        result = self._expr_rest(rest, self._term(term))
        node.attrs["type"] = result
        return result

    # (14) Expr' → + Term Expr'1     Expr'1.inh := arithmetic(+, Expr'.inh, Term.type)
    # (15) Expr' → - Term Expr'1     igual con -
    # (16) Expr' → ε                 Expr'.syn := Expr'.inh
    def _expr_rest(self, node: Node, inherited: str) -> str:
        node.attrs["inh"] = inherited
        if node.production.number == 16:
            node.attrs["syn"] = inherited
            return inherited
        op, term, rest = node.children
        combined = self._binary(op, inherited, self._term(term))
        result = self._expr_rest(rest, combined)
        node.attrs["syn"] = result
        return result

    # (17) Term → Factor Term'       Term'.inh := Factor.type;  Term.type := Term'.syn
    def _term(self, node: Node) -> str:
        factor, rest = node.children
        result = self._term_rest(rest, self._factor(factor))
        node.attrs["type"] = result
        return result

    # (18) Term' → * Factor Term'1   (19) con /   (20) con %   (21) Term' → ε
    def _term_rest(self, node: Node, inherited: str) -> str:
        node.attrs["inh"] = inherited
        if node.production.number == 21:
            node.attrs["syn"] = inherited
            return inherited
        op, factor, rest = node.children
        combined = self._binary(op, inherited, self._factor(factor))
        result = self._term_rest(rest, combined)
        node.attrs["syn"] = result
        return result

    def _binary(self, op_node: Node, left: str, right: str) -> str:
        result, message = arithmetic(op_node.symbol, left, right)
        if message:
            self._error(op_node.token.line, message)
        return result

    # (22) Factor → ( Expr )         Factor.type := Expr.type
    # (23) Factor → - Factor1        Factor.type := negate(Factor1.type)
    # (24) Factor → id               Factor.type := lookup(id).type, Use the declared type or report an undeclared identifier.
    # (25) num → int   (26) real → float   (27) chr → char
    def _factor(self, node: Node) -> str:
        number = node.production.number
        if number == 22:
            result = self._expr(node.children[1])
        elif number == 23:
            minus, operand = node.children
            result, message = negate(self._factor(operand))
            if message:
                self._error(minus.token.line, message)
        elif number == 24:
            token = node.children[0].token
            entry = self.symbols.lookup(token.lexeme)
            if entry is None or entry.type == UNDECLARED:
                self._error(token.line, f"'{token.lexeme}' is not declared")
                result = ERROR
            else:
                result = entry.type
        else:
            result = CONSTANT_TYPE[node.children[0].symbol]
        node.attrs["type"] = result
        return result
