"""Predictive LL(1) Parsing table M[A, a] built from FIRST and FOLLOW sets."""

import csv
import io
from pathlib import Path

from .grammar import END, EPSILON, Grammar, Production

TABLE_PATH = Path(__file__).resolve().parent.parent / "data" / "ll1_table.csv"

# Column order: types, operands, operators, punctuation, and the end marker.
COLUMN_ORDER = ["int", "float", "char", "id", "num", "real", "chr",
                "=", "+", "-", "*", "/", "%", "(", ")", ";", END]


class LL1Conflict(Exception):
    """Raised when two different productions are assigned to the same cell."""


class LL1Table:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        known = [t for t in COLUMN_ORDER if t in grammar.terminals or t == END]
        self.columns = known + [t for t in grammar.terminals if t not in known]
        self.cells: dict[tuple[str, str], Production] = {}
        for p in grammar.productions:
            first = grammar.first_of_sequence(p.body)
            for a in first - {EPSILON}:
                self._place(p, a)
            if EPSILON in first:
                for b in grammar.follow[p.head]:
                    self._place(p, b)

    def _place(self, p: Production, terminal: str) -> None:
        key = (p.head, terminal)
        if key in self.cells and self.cells[key] != p:
            raise LL1Conflict(
                f"Conflict at M[{p.head}, {terminal}]: "
                f"productions {self.cells[key].number} and {p.number}."
            )
        self.cells[key] = p

    def get(self, nonterminal: str, terminal: str) -> Production | None:
        return self.cells.get((nonterminal, terminal))

    def expected(self, nonterminal: str) -> list[str]:
        """Return the terminals with entries in the given nonterminal's row."""
        return [a for a in self.columns if (nonterminal, a) in self.cells]

    def to_csv(self) -> str:
        out = io.StringIO()
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(["nonterminal", *self.columns])
        for a in self.grammar.nonterminals:
            row = [a]
            for t in self.columns:
                p = self.cells.get((a, t))
                row.append(str(p.number) if p else "")
            writer.writerow(row)
        return out.getvalue()
