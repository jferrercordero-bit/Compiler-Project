"""Automated tests for the LL(1) parser and SDT evaluator.

Run from the repository root:
    python -m unittest discover -s tests -v
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from lexer.model.symbol_table import SymbolTable  # noqa: E402
from parser.controller.parser_controller import ParserController  # noqa: E402
from parser.model.grammar import END, EPSILON, Grammar  # noqa: E402
from parser.model.ll1_parser import LL1Parser, ParseError  # noqa: E402
from parser.model.ll1_table import TABLE_PATH, LL1Table  # noqa: E402
from parser.model.sdt import SDTEvaluator  # noqa: E402
from parser.model.token_adapter import adapt  # noqa: E402
from parser.model.type_system import arithmetic, assignable  # noqa: E402
from parser.view.output_formatter import OutputFormatter  # noqa: E402
import parse  # noqa: E402

SAMPLES = ROOT / "samples" / "parser"
CONTROLLER = ParserController()
GRAMMAR = CONTROLLER.grammar
TABLE = CONTROLLER.table


def run(text, trace=False):
    return CONTROLLER.run(text, trace=trace)


def output(text):
    return OutputFormatter().format(run(text))


def errors(result):
    return [(e.line, e.message) for e in result.sdt_errors]


class GrammarDesign(unittest.TestCase):
    """Check the grammar and its FIRST and FOLLOW sets against Steps 3, 5, and 6 of the design."""

    def test_four_tuple(self):
        self.assertEqual(GRAMMAR.start, "Program")
        self.assertEqual(len(GRAMMAR.productions), 27)
        self.assertEqual(GRAMMAR.nonterminals, ["Program", "StmtList", "Stmt", "Decl", "Decl'",
                                                "Assign", "Type", "Expr", "Expr'", "Term",
                                                "Term'", "Factor"])
        self.assertEqual(set(GRAMMAR.terminals), {"int", "float", "char", "id", "num", "real", "chr",
                                                  "=", "+", "-", "*", "/", "%", "(", ")", ";"})

    def test_first_sets(self):
        operand = {"id", "num", "real", "chr", "-", "("}
        expected = {
            "Program": {"int", "float", "char", "id"},
            "StmtList": {"int", "float", "char", "id", EPSILON},
            "Stmt": {"int", "float", "char", "id"},
            "Decl": {"int", "float", "char"},
            "Decl'": {";", "="},
            "Assign": {"id"},
            "Type": {"int", "float", "char"},
            "Expr": operand, "Term": operand, "Factor": operand,
            "Expr'": {"+", "-", EPSILON},
            "Term'": {"*", "/", "%", EPSILON},
        }
        for nonterminal, first in expected.items():
            self.assertEqual(GRAMMAR.first[nonterminal], first, nonterminal)

    def test_follow_sets(self):
        statement_end = {"int", "float", "char", "id", END}
        expected = {
            "Program": {END}, "StmtList": {END},
            "Stmt": statement_end, "Decl": statement_end, "Decl'": statement_end,
            "Assign": statement_end,
            "Type": {"id"},
            "Expr": {";", ")"}, "Expr'": {";", ")"},
            "Term": {"+", "-", ";", ")"}, "Term'": {"+", "-", ";", ")"},
            "Factor": {"*", "/", "%", "+", "-", ";", ")"},
        }
        for nonterminal, follow in expected.items():
            self.assertEqual(GRAMMAR.follow[nonterminal], follow, nonterminal)

    def test_no_left_recursion(self):
        for p in GRAMMAR.productions:
            self.assertFalse(p.body and p.body[0] == p.head, str(p))


class LL1TableDesign(unittest.TestCase):

    def test_table_has_no_conflicts_and_51_entries(self):
        self.assertEqual(len(TABLE.cells), 51)  # LL1Table raises LL1Conflict if it finds a conflict.

    def test_generated_table_matches_designer_csv(self):
        # Compare the generated table with the Model Designer's reference CSV.
        self.assertEqual(TABLE.to_csv(), TABLE_PATH.read_text(encoding="utf-8"))

    def test_epsilon_productions_go_under_follow(self):
        self.assertEqual(TABLE.get("StmtList", END).number, 3)
        for t in (";", ")"):
            self.assertEqual(TABLE.get("Expr'", t).number, 16)
        for t in ("+", "-", ";", ")"):
            self.assertEqual(TABLE.get("Term'", t).number, 21)

    def test_conflict_is_detected(self):
        from parser.model.grammar import Production
        from parser.model.ll1_table import LL1Conflict
        # This simplified G0 example shows two Decl productions with a common prefix before left factoring.
        g0 = Grammar([Production(1, "Decl", ("int", "id", ";")),
                      Production(2, "Decl", ("int", "id", "=", "num", ";"))])
        with self.assertRaises(LL1Conflict):
            LL1Table(g0)


class Parsing(unittest.TestCase):

    def test_assignment_example(self):
        r = run("int x = 10;")
        self.assertTrue(r.parsing_ok)
        self.assertTrue(r.sdt_ok)
        self.assertEqual([leaf.symbol for leaf in r.tree.leaves()], ["int", "id", "=", "num", ";"])

    def test_trace_of_example_has_17_steps_and_accepts(self):
        r = run("int x = 10;", trace=True)
        self.assertEqual(len(r.trace), 17)
        self.assertEqual(r.trace[0].stack, "$ Program")
        self.assertEqual(r.trace[3].stack, "$ StmtList Decl' id Type")
        self.assertEqual(r.trace[-1].action, "accept")

    def test_valid_program(self):
        r = run((SAMPLES / "valid_program.c").read_text(encoding="utf-8"))
        self.assertTrue(r.sdt_ok, errors(r))

    def test_tree_root_and_production_numbers(self):
        r = run("x = 1;")
        self.assertEqual(r.tree.symbol, "Program")
        self.assertEqual(r.tree.production.number, 1)
        self.assertEqual(r.tree.children[0].production.number, 5)  # Stmt → Assign

    def test_missing_semicolon_at_end_of_input(self):
        r = run("int x = 10")
        self.assertFalse(r.parsing_ok)
        self.assertEqual((r.syntax_error.line, r.syntax_error.message), (1, "missing ';' after '10'"))

    def test_missing_semicolon_is_reported_on_its_own_line(self):
        r = run((SAMPLES / "syntax_error.c").read_text(encoding="utf-8"))
        self.assertEqual((r.syntax_error.line, r.syntax_error.message), (1, "missing ';' after '10'"))

    def test_unexpected_token_lists_the_table_row(self):
        r = run("int x 10;")
        self.assertEqual(r.syntax_error.message, "unexpected '10', expected '=' or ';'")

    def test_unbalanced_parenthesis(self):
        r = run("int x = (10;")
        self.assertEqual(r.syntax_error.message, "unexpected ';', expected ')'")

    def test_token_outside_the_grammar(self):
        r = run("return 0;")
        self.assertIn("unexpected 'return'", r.syntax_error.message)

    def test_empty_input(self):
        r = run("")
        self.assertIn("unexpected end of input", r.syntax_error.message)

    def test_error_is_found_on_a_later_line(self):
        r = run("int a = 1;\nint b = 2;\nint c = = 3;\n")
        self.assertEqual(r.syntax_error.line, 3)

    def test_lexical_error_stops_the_parser(self):
        r = run((SAMPLES / "lexical_error.c").read_text(encoding="utf-8"))
        self.assertFalse(r.parsing_ok)
        self.assertFalse(r.sdt_ok)
        self.assertIsNone(r.tree)

    def test_parser_raises_with_line(self):
        parser = LL1Parser(TABLE)
        with self.assertRaises(ParseError):
            parser.parse(adapt(CONTROLLER.lexer.run("int ;").tokens))


class SDTRules(unittest.TestCase):

    def test_widening_int_to_float_is_allowed(self):
        self.assertTrue(run("float f = 10;").sdt_ok)

    def test_narrowing_float_to_int_fails(self):
        r = run("int x = 3.14;")
        self.assertTrue(r.parsing_ok)
        self.assertEqual(errors(r), [(1, "type mismatch: 'x' is int but the value is float")])

    def test_parsing_success_but_sdt_error_sample(self):
        r = run((SAMPLES / "sdt_error.c").read_text(encoding="utf-8"))
        self.assertTrue(r.parsing_ok)
        self.assertEqual(errors(r), [(3, "type mismatch: 'x' is int but the value is float")])

    def test_every_semantic_rule(self):
        r = run((SAMPLES / "semantic_errors.c").read_text(encoding="utf-8"))
        self.assertTrue(r.parsing_ok)
        self.assertEqual(errors(r), [
            (1, "'y' is not declared"),
            (2, "'x' is already declared in line 1"),
            (3, "operator '%' needs int operands, found float and int"),
            (4, "operator '+' needs numeric operands, found char and int"),
            (5, "'z' is not declared"),
            (6, "unary '-' needs a numeric operand, found char"),
            (7, "type mismatch: 'd' is char but the value is int"),
            (8, "type mismatch: 'm' is int but the value is float"),
        ])

    def test_error_type_does_not_cascade(self):
        # Report one error for the undeclared y and suppress follow-on errors from the addition and initialization.
        self.assertEqual(len(run("int x = y + 1 * 2;").sdt_errors), 1)

    def test_variable_is_not_visible_in_its_own_initializer(self):
        self.assertEqual(errors(run("int x = x;")), [(1, "'x' is not declared")])

    def test_use_before_declaration(self):
        self.assertEqual(errors(run("x = 1;\nint x;")), [(1, "'x' is not declared")])

    def test_types_propagate_through_expressions(self):
        r = run("int a = 1;\nfloat b = (a + 2) * 0.5;")
        self.assertTrue(r.sdt_ok)
        # Follow the tree from Program through StmtList, Stmt, Decl, and Decl' to the initializer Expr.
        expr = r.tree.children[1].children[0].children[0].children[2].children[1]
        self.assertEqual(expr.symbol, "Expr")
        self.assertEqual(expr.attrs["type"], "float")

    def test_symbol_table_types_sizes_and_addresses(self):
        r = run("int a;\nfloat b;\nchar c;\nint d;")
        table = {e.name: (e.type, e.size, e.address) for e in r.symbols.entries()}
        self.assertEqual(table, {"a": ("int", 4, 0), "b": ("float", 4, 4),
                                 "c": ("char", 1, 8), "d": ("int", 4, 9)})

    def test_type_system(self):
        self.assertEqual(arithmetic("+", "int", "float"), ("float", None))
        self.assertEqual(arithmetic("/", "int", "int"), ("int", None))
        self.assertEqual(arithmetic("+", "error", "char"), ("error", None))
        self.assertTrue(assignable("float", "int"))
        self.assertFalse(assignable("int", "float"))
        self.assertFalse(assignable("char", "int"))

    def test_evaluator_with_fresh_symbol_table(self):
        tree = LL1Parser(TABLE).parse(adapt(CONTROLLER.lexer.run("int a = 1;").tokens))
        symbols = SymbolTable()
        self.assertEqual(SDTEvaluator(symbols).evaluate(tree), [])
        self.assertEqual(symbols.lookup("a").type, "int")


class Outputs(unittest.TestCase):
    """Check the three output cases from Step 12 of the design against the assignment's requirements."""

    def test_success(self):
        self.assertEqual(output("int x = 10;"),
                         "Input tokens:\n  1: int id = num ;\nParsing Success!\nSDT Verified!")

    def test_parsing_error(self):
        self.assertEqual(output("int x = 10").splitlines()[2:],
                         ["Parsing error...", "SDT error...", "error in line 1: missing ';' after '10'"])

    def test_parsing_success_sdt_error(self):
        self.assertEqual(output("int x = 3.14;").splitlines()[2:],
                         ["Parsing Success!", "SDT error...",
                          "error in line 1: type mismatch: 'x' is int but the value is float"])

    def test_lexical_error_output(self):
        self.assertIn("error in line 1: lexical error: unexpected character '@'",
                      output("int @x = 10;"))

    def test_cli_options_and_exit_codes(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            ok = parse.main(["--text", "int x = 10;", "--trace", "--tree", "--symbols"])
        text = buffer.getvalue()
        self.assertEqual(ok, 0)
        for piece in ("accept", "Annotated parse tree", "Decl'  [inh=int]", "Symbol table"):
            self.assertIn(piece, text)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parse.main(["--text", "int x = 3.14;"]), 1)
            self.assertEqual(parse.main(["--text", "int x = 10"]), 1)

    def test_cli_file_option(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.c"
            path.write_text("int x = 10;\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.assertEqual(parse.main(["--file", str(path)]), 0)
        self.assertIn("SDT Verified!", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
