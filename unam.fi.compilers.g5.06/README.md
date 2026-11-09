# unam.fi.compilers.g5.06 — Lexer, Parser, and SDT

A compiler for a subset of C, developed for the Compilers course (Group 5, UNAM Faculty of Engineering). It has two phases implemented using the theory covered in class, without FLEX or libraries for regular expressions or parsing.

1. **Lexer:** regular expressions → NFA → 25-state DFA → transition table.
2. **Parser and SDT:** LL(1) grammar with 27 productions → FIRST and FOLLOW sets → LL(1) table → stack-based predictive parser that builds the parse tree → SDT rules for type checking and declarations.

Requires Python 3.10 or later. There are no external dependencies.

## Parser & SDT

```bash
python parse.py --text "int x = 10;"
python parse.py --file samples/parser/valid_program.c --tree --symbols
python parse.py --file samples/parser/example.c --trace
```

Output for `int x = 10;`

```
Input tokens:
  1: int id = num ;
Parsing Success!
SDT Verified!
```

The other two possible outcomes are shown below.

```
Parsing error...                     Parsing Success!
SDT error...                         SDT error...
error in line 1: missing ';' ...     error in line 3: type mismatch: 'x' is int but the value is float
```

The `--trace` option shows the LL(1) parsing trace, including the stack, remaining input, and action. The `--tree` option shows the parse tree annotated with SDT attributes, and `--symbols` shows the symbol table with types, sizes, and addresses.

The program exits with code 0 if both parsing and SDT verification succeed, and with code 1 otherwise.

## Lexer

```bash
python main.py --text "int a = 10;"
python main.py --file samples/class_example.c --detail
```

The lexer recognizes 45 token types across 7 categories and skips whitespace and comments.

## Project Structure

```
main.py                         Lexer entry point
parse.py                        Parser and SDT entry point
src/lexer/                      DFA, transition table, symbol table, and lexical errors
src/parser/
  data/grammar.txt              Grammar with 27 productions (Model Designer)
  data/ll1_table.csv             LL(1) table (Model Designer)
  model/                        grammar, ll1_table, token_adapter, ll1_parser,
                                parse_tree, type_system, sdt
  view/                         input_reader, output_formatter
  controller/                   parser_controller (lexer → parser → SDT)
samples/                        Lexer input samples
samples/parser/                 Parser input samples: valid input, syntax error, and SDT errors
tests/                          71 automated tests (33 for the lexer and 38 for the parser)
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Team

| Role | Team Member |
| --- | --- |
| Project Manager | Ferrer Cordero José Manuel|
| Model Designer | Vidrio Lopez Mario Alexis |
| Developer | González Casimiro Juan Carlos |
| Writer | Ambriz Cano Diego Emilio |
| Presenter | Casillas Juárez Camila |

