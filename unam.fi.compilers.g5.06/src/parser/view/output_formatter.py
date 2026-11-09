"""Format the output required by the assignment (Step 12 )."""

from itertools import groupby

from ..controller.parser_controller import ParseResult

PARSING_SUCCESS = "Parsing Success!"
PARSING_ERROR = "Parsing error..."
SDT_VERIFIED = "SDT Verified!"
SDT_ERROR = "SDT error..."


class OutputFormatter:
    def format(self, result: ParseResult, trace: bool = False, tree: bool = False,
               symbols: bool = False) -> str:
        lines = ["Input tokens:"]
        if result.input:
            for line, group in groupby(result.input, key=lambda s: s.line):
                lines.append(f"  {line}: " + " ".join(s.terminal for s in group))
        else:
            lines.append("  (empty)")

        if trace and result.trace:
            lines += ["", self._trace(result), ""]

        lines.append(PARSING_SUCCESS if result.parsing_ok else PARSING_ERROR)
        lines.append(SDT_VERIFIED if result.sdt_ok else SDT_ERROR)
        for error in result.lexical_errors:
            lines.append(f"error in line {error.line}: lexical error: {error.message}")
        if result.syntax_error:
            lines.append(f"error in line {result.syntax_error.line}: {result.syntax_error.message}")
        for error in result.sdt_errors:
            lines.append(f"error in line {error.line}: {error.message}")

        if tree and result.tree is not None:
            lines += ["", "Annotated parse tree", result.tree.render()]
        if symbols and result.parsing_ok and len(result.symbols):
            lines += ["", "Symbol table", self._symbols(result)]
        return "\n".join(lines)

    @staticmethod
    def _trace(result: ParseResult) -> str:
        rows = [("Step", "Stack", "Input", "Action")]
        rows += [(str(r.step), r.stack, r.input, r.action) for r in result.trace]
        widths = [max(len(row[i]) for row in rows) for i in range(3)]
        out = []
        for k, row in enumerate(rows):
            out.append("  ".join(cell.ljust(widths[i]) if i < 3 else cell
                                 for i, cell in enumerate(row)).rstrip())
            if k == 0:
                out.append("  ".join("-" * w for w in widths) + "  " + "-" * 6)
        return "\n".join(out)

    @staticmethod
    def _symbols(result: ParseResult) -> str:
        out = [f"{'Name':<12}{'Type':<7}{'Size':<6}{'Dimension':<11}{'Lines':<12}Address"]
        for e in result.symbols.entries():
            used = ",".join(str(n) for n in e.lines)
            out.append(f"{e.name:<12}{e.type:<7}{e.size!s:<6}{e.dimension!s:<11}{used:<12}{e.address}")
        return "\n".join(out)
