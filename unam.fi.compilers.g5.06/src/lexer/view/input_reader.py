"""Lee la entrada: una cadena (--text), un archivo (--file) o, si no hay ninguno, la entrada estándar."""

import argparse
import sys
from pathlib import Path


class InputReader:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="python main.py",
            description="Analizador léxico de unam.fi.compilers.g5.XX",
        )
        source = self.parser.add_mutually_exclusive_group()
        source.add_argument("--text", help="cadena a escanear")
        source.add_argument("--file", help="ruta del archivo a escanear")
        self.parser.add_argument(
            "--detail",
            action="store_true",
            help="muestra TokenType, línea y columna de cada token, y la tabla de símbolos",
        )

    def read(self, argv: list[str] | None = None) -> tuple[str, argparse.Namespace]:
        options = self.parser.parse_args(argv)
        if options.text is not None:
            return options.text, options
        if options.file is not None:
            return Path(options.file).read_text(encoding="utf-8"), options
        return sys.stdin.read(), options
