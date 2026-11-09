"""Read source code from a string (--text), a file (--file), or standard input."""

import argparse
import sys
from pathlib import Path


class InputReader:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="python parse.py",
            description="LL(1) parser and SDT evaluator for unam.fi.compilers.g5.06",
        )
        source = self.parser.add_mutually_exclusive_group()
        source.add_argument("--text", help="Source code to analyze")
        source.add_argument("--file", help="Path to the source file")
        self.parser.add_argument("--trace", action="store_true",
                                 help="Show the LL(1) parser trace with the stack, remaining input, and action")
        self.parser.add_argument("--tree", action="store_true",
                                 help="Show the parse tree annotated with semantic attributes")
        self.parser.add_argument("--symbols", action="store_true",
                                 	help="Show the symbol table after semantic analysis")

    def read(self, argv: list[str] | None = None) -> tuple[str, argparse.Namespace]:
        options = self.parser.parse_args(argv)
        if options.text is not None:
            return options.text, options
        if options.file is not None:
            return Path(options.file).read_text(encoding="utf-8"), options
        return sys.stdin.read(), options
