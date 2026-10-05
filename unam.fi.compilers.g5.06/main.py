"""Start the lexer from the command line.
Usage:

    python main.py --text "int a = 10;"
    python main.py --file samples/example1.c
    python main.py --file samples/class_example.c --detail
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from lexer.controller.lexer_controller import LexerController
from lexer.view.input_reader import InputReader
from lexer.view.output_formatter import OutputFormatter 


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text, options = InputReader().read(argv)
    result = LexerController().run(text)
    print(OutputFormatter().format(result, detail=options.detail))
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
