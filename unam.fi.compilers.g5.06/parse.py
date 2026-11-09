"""Start point of Parser and SDT.

    python parse.py --text "int x = 10;"
    python parse.py --file samples/parser/valid_program.c --tree --symbols
    python parse.py --file samples/parser/example.c --trace
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from parser.controller.parser_controller import ParserController  # noqa: E402
from parser.view.input_reader import InputReader  # noqa: E402
from parser.view.output_formatter import OutputFormatter  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8") 
    text, options = InputReader().read(argv)
    result = ParserController().run(text, trace=options.trace)
    print(OutputFormatter().format(result, trace=options.trace, tree=options.tree,
                                   symbols=options.symbols))
    return 0 if result.sdt_ok else 1


if __name__ == "__main__":
    sys.exit(main())
