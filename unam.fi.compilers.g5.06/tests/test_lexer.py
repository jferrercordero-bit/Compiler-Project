"""Automated tests for the lexer.

Execute from the repository root:
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

from lexer.controller.lexer_controller import LexerController  # noqa: E402
from lexer.model.char_class import CLASSES, char_class  # noqa: E402
from lexer.model.symbol_table import SymbolTable  # noqa: E402
from lexer.model.token_type import TokenClass, TokenType  # noqa: E402
from lexer.model.transition_table import FINAL_STATES, TransitionTable  # noqa: E402
from lexer.view.output_formatter import OutputFormatter  # noqa: E402
import main  # noqa: E402

SAMPLES = ROOT / "samples"
CONTROLLER = LexerController()


def lex(text):
    return CONTROLLER.run(text)


def stream(result):
    return " ".join(t.token_class.label for t in result.tokens)


def types(result):
    return [t.type for t in result.tokens]


class ReadingExamples(unittest.TestCase):
    """T1 to T8: test cases from the assignment and the report."""

    def test_t1_printf_example(self):
        r = lex('printf("This is an example");')
        self.assertEqual(stream(r), "identifier punctuation literal punctuation punctuation")
        self.assertEqual(len(r.tokens), 5)

    def test_t2_declaration_example(self):
        r = lex("int a = 10;")
        self.assertEqual(stream(r), "keyword identifier operator constant punctuation")
        self.assertEqual(types(r), [TokenType.INT, TokenType.ID, TokenType.ASSIGN,
                                    TokenType.INT_CONST, TokenType.SEMI])

    def test_t3_both_examples(self):
        r = lex('printf("This is an example");\nint a = 10;\n')
        self.assertEqual(len(r.tokens), 10)

    def test_t4_class_program_has_39_tokens(self):
        r = lex((SAMPLES / "class_example.c").read_text(encoding="utf-8"))
        self.assertEqual(len(r.tokens), 39)
        counts = {c: sum(t.token_class is c for t in r.tokens) for c in TokenClass}
        self.assertEqual(counts[TokenClass.KEYWORD], 3)
        self.assertEqual(counts[TokenClass.IDENTIFIER], 11)
        self.assertEqual(counts[TokenClass.OPERATOR], 6)
        self.assertEqual(counts[TokenClass.CONSTANT], 4)
        self.assertEqual(counts[TokenClass.LITERAL], 1)
        self.assertEqual(counts[TokenClass.PUNCTUATION], 14)

    def test_t5_print_is_keyword(self):
        r = lex("print x;")
        self.assertEqual(stream(r), "keyword identifier punctuation")
        self.assertIs(r.tokens[0].type, TokenType.PRINT)

    def test_t6_comment_is_discarded(self):
        r = lex("x = 5; // set x")
        self.assertEqual(stream(r), "identifier operator constant punctuation")

    def test_t7_scanning_continues_after_error(self):
        r = lex("int @a = 10;")
        self.assertEqual(stream(r), "keyword identifier operator constant punctuation")
        self.assertEqual(str(r.errors[0]), "Lexical error 1:5: unexpected character '@'")

    def test_t8_typographic_quotes_are_normalized(self):
        r = lex("printf(\u201cThis is an example\u201d);")
        self.assertEqual(stream(r), "identifier punctuation literal punctuation punctuation")
        self.assertEqual(r.tokens[2].lexeme, '"This is an example"')


class NewTokenKinds(unittest.TestCase):
    """T9 to T13: chars, booleans, escapes and full catalog."""

    def test_t9_char_constant(self):
        r = lex("char c = 'a';")
        self.assertEqual(stream(r), "keyword identifier operator constant punctuation")
        self.assertIs(r.tokens[3].type, TokenType.CHAR_CONST)

    def test_t10_boolean_from_lookup_table(self):
        r = lex("x = false;")
        self.assertEqual(stream(r), "identifier operator constant punctuation")
        self.assertIs(r.tokens[2].type, TokenType.FALSE)

    def test_t11_escapes_do_not_close_string(self):
        r = lex('printf("a \\"b\\"");')
        self.assertEqual(stream(r), "identifier punctuation literal punctuation punctuation")
        self.assertEqual(r.tokens[2].lexeme, '"a \\"b\\""')

    def test_t12_malformed_char_is_skipped_whole(self):
        r = lex("char c = 'ab';")
        self.assertEqual(stream(r), "keyword identifier operator punctuation")
        self.assertEqual(str(r.errors[0]), "Lexical error 1:10: malformed character constant")

    def test_t13_all_45_token_types_once(self):
        r = lex((SAMPLES / "all_tokens.c").read_text(encoding="utf-8"))
        self.assertEqual(len(r.tokens), 45)
        self.assertEqual(types(r), list(TokenType))
        self.assertEqual(r.errors, [])


class PriorityRules(unittest.TestCase):
    """Test for the five Priority rules."""

    def test_rule1_longest_match(self):
        r = lex("a<=b==c!=d&&e||f")
        ops = [t.lexeme for t in r.tokens if t.token_class is TokenClass.OPERATOR]
        self.assertEqual(ops, ["<=", "==", "!=", "&&", "||"])
        self.assertIs(lex("printf").tokens[0].type, TokenType.ID)
        self.assertIs(lex("3.14").tokens[0].type, TokenType.FLOAT_CONST)

    def test_rule1_backtracking(self):
        r = lex("5.x")
        self.assertEqual([t.lexeme for t in r.tokens], ["5", ".", "x"])
        self.assertEqual(types(r), [TokenType.INT_CONST, TokenType.DOT, TokenType.ID])

    def test_rule2_lookup_table_wins(self):
        self.assertIs(lex("int").tokens[0].type, TokenType.INT)
        self.assertIs(lex("true").tokens[0].type, TokenType.TRUE)
        self.assertIs(lex("trueValue").tokens[0].type, TokenType.ID)
        self.assertIs(lex("ifx").tokens[0].type, TokenType.ID)

    def test_rule3_whitespace_and_comments_are_not_tokens(self):
        r = lex("  /* a ** b */ x\t// fin\n  y  ")
        self.assertEqual([t.lexeme for t in r.tokens], ["x", "y"])
        self.assertEqual(r.errors, [])

    def test_rule4_unterminated_comment_is_not_slash(self):
        r = lex("x = 1; /* sin cerrar")
        self.assertEqual([t.lexeme for t in r.tokens], ["x", "=", "1", ";"])
        self.assertEqual(str(r.errors[0]), "Lexical error 1:8: unterminated comment")

    def test_rule5_no_default_token(self):
        r = lex("$")
        self.assertEqual(r.tokens, [])
        self.assertEqual(len(r.errors), 1)

    def test_constants_have_no_sign(self):
        r = lex("a-1")
        self.assertEqual(types(r), [TokenType.ID, TokenType.MINUS, TokenType.INT_CONST])


class ErrorsAndPositions(unittest.TestCase):

    def test_unterminated_string_skips_to_end_of_line(self):
        r = lex('s = "abc\nx;')
        self.assertEqual([t.lexeme for t in r.tokens], ["s", "=", "x", ";"])
        self.assertEqual(str(r.errors[0]), "Lexical error 1:5: unterminated string literal")

    def test_several_errors_in_one_run(self):
        r = lex((SAMPLES / "errors.c").read_text(encoding="utf-8"))
        self.assertEqual([str(e) for e in r.errors], [
            "Lexical error 1:5: unexpected character '@'",
            "Lexical error 2:10: malformed character constant",
            "Lexical error 3:8: unterminated string literal",
            "Lexical error 4:8: unterminated comment",
        ])

    def test_line_and_column(self):
        r = lex("int a;\n  b = 2;")
        self.assertEqual([(t.line, t.column) for t in r.tokens],
                         [(1, 1), (1, 5), (1, 6), (2, 3), (2, 5), (2, 7), (2, 8)])

    def test_symbol_table_records_lines(self):
        r = lex("x = 1;\ny = x;\nx = y;")
        self.assertEqual(r.symbols.lookup("x").lines, [1, 2, 3])
        self.assertEqual(r.symbols.lookup("y").lines, [2, 3])
        self.assertIsNone(r.symbols.lookup("int"))
        self.assertEqual(r.symbols.lookup("x").type, "TBD")

    def test_empty_symbol_table_is_used(self):
        from lexer.model.scanner import Scanner
        table = SymbolTable()
        Scanner(symbols=table).scan("abc")
        self.assertIsNotNone(table.lookup("abc"))


class ModelIntegrity(unittest.TestCase):
    """Verifies that the code is consistent with the Model Designer's specification."""

    def test_catalog_has_45_types_numbered_in_order(self):
        self.assertEqual([t.number for t in TokenType], list(range(1, 46)))

    def test_transition_table_shape(self):
        table = TransitionTable()
        self.assertEqual(table.states, [f"q{i}" for i in range(25)])
        for state in table.states:
            row = table.row(state)
            self.assertEqual(tuple(row), CLASSES)
            for target in row.values():
                self.assertTrue(target is None or target in table.states)
        self.assertTrue(FINAL_STATES <= set(table.states))
        self.assertEqual(len(FINAL_STATES), 16)

    def test_char_classes(self):
        expected = {"a": "L", "_": "L", "7": "D", "'": "APOS", "\\": "BSLASH",
                    "\n": "NL", "\t": "WS", "@": "OTHER", "\u00e1": "OTHER"}
        for ch, cls in expected.items():
            self.assertEqual(char_class(ch), cls)

    def test_no_regex_library_is_used(self):
        for source in (ROOT / "src").rglob("*.py"):
            text = source.read_text(encoding="utf-8")
            self.assertNotIn("import re", text, source.name)
            self.assertNotIn("from re ", text, source.name)


class InputAndOutput(unittest.TestCase):

    def test_output_format_matches_assignment(self):
        out = OutputFormatter().format(lex("int a = 10;"))
        self.assertEqual(out, "\n".join([
            "keyword identifier operator constant punctuation",
            "Keyword: int",
            "Identifier: a",
            "Operator: =",
            "Constant: 10",
            "Punctuation: ;",
            "Total of tokens: 5",
        ]))

    def test_cli_text_option(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main.main(["--text", "print x;"])
        self.assertEqual(code, 0)
        self.assertIn("Keyword: print", buffer.getvalue())
        self.assertIn("Total of tokens: 3", buffer.getvalue())

    def test_cli_file_option(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.c"
            path.write_text("int a = 10;\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main.main(["--file", str(path)])
        self.assertEqual(code, 0)
        self.assertTrue(buffer.getvalue().rstrip().endswith("Total of tokens: 5"))

    def test_cli_returns_1_when_there_are_errors(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main.main(["--text", "int @a;"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
