"""Read input from command line, file or standard input."""

import argparse
import sys
from pathlib import Path


class InputReader:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="python main.py",
            description="Lexical analyzer for unam.fi.compilers.g5.06",
        )
        source = self.parser.add_mutually_exclusive_group()
        source.add_argument("--text", help="text to scan")
        source.add_argument("--file", help="path to the input file")
        self.parser.add_argument(
            "--detail",
            action="store_true",
            help="shows the TokenType, line, and column of each token, as well as the symbol table",
        )

    def read(self, argv: list[str] | None = None) -> tuple[str, argparse.Namespace]:
        options = self.parser.parse_args(argv)
        if options.text is not None:
            return options.text, options
        if options.file is not None:
            return Path(options.file).read_text(encoding="utf-8"), options
        return sys.stdin.read(), options
