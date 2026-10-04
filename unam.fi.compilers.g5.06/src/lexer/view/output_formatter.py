"""Output format required in the assignment: sequence, one line per token and total."""

from ..controller.lexer_controller import LexResult


class OutputFormatter:
    def format(self, result: LexResult, detail: bool = False) -> str:
        lines = [" ".join(t.token_class.label for t in result.tokens)]
        for t in result.tokens:
            entry = f"{t.token_class.title}: {t.lexeme}"
            if detail:
                entry += f"    [{t.type.name}, {t.line}:{t.column}]"
            lines.append(entry)
        lines.append(f"Total of tokens: {len(result.tokens)}")
        if result.errors:
            lines.append("")
            lines.extend(str(error) for error in result.errors)
        if detail and len(result.symbols):
            lines.append("")
            lines.append("Symbol table")
            lines.append(f"{'Name':<12}{'Type':<6}{'Size':<6}{'Dimension':<11}{'Lines':<12}Address")
            for e in result.symbols.entries():
                used = ",".join(str(n) for n in e.lines)
                lines.append(f"{e.name:<12}{e.type:<6}{e.size:<6}{e.dimension:<11}{used:<12}{e.address}")
        return "\n".join(lines)
