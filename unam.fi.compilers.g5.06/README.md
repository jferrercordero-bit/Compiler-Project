# unam.fi.compilers.g5.06 — Lexical Analyzer

Lexer for a subset of the C language, developed for the Compilers course (Group 5, FI UNAM).
The program was built using only the concepts seen in class: regex → NFA → DFA →
transition table. It does not use FLEX or any regex libraries either.


## Quick start

Requirements: Python 3.10 or later. No additional dependences are required.

```bash
python main.py --text "int a = 10;"
python main.py --file samples/example1.c
python main.py --file samples/class_example.c --detail
```

Output for `int a = 10;`:

```
keyword identifier operator constant punctuation
Keyword: int
Identifier: a
Operator: =
Constant: 10
Punctuation: ;
Total of tokens: 5
```

Without `--text` or `--file`, the program reads from the standard input. With `--detail`  the output shows the TokenType, its line and column, and the symbol table as well.
The program exits with code 1 if there are any lexical errors, 0 otherwise.

## What it recognizes

45 token types divided into 7 classes: keyword, identifier, constant (integers,
floats, characters and booleans), literal (string with escapes), operator, punctuation
and special characters. Whitespaces and comments are recognized and discarded.
Lexical errors are reported with the line and column and the scanning continues afterward.

## Structure

```
main.py                         entry point
src/lexer/
  data/transition_table.csv     25 state-DFA × 18 classes (design by the Model Designer)
  model/                        token_type, token, char_class, transition_table,
                                preprocessor, scanner, token_classifier,
                                symbol_table, error_handler
  view/                         input_reader, output_formatter
  controller/                   lexer_controller
samples/                        input examples, class program, 45 tokens, errors
tests/test_lexer.py             33 automated tests
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
