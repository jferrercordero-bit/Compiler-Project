"""Context-free grammar G = (N, T, P, S) and its FIRST and FOLLOW sets."""

from dataclasses import dataclass
from pathlib import Path

EPSILON = "ε"
END = "$"
GRAMMAR_PATH = Path(__file__).resolve().parent.parent / "data" / "grammar.txt"


@dataclass(frozen=True)
class Production:
    number: int
    head: str
    body: tuple[str, ...]  	# An empty tuple represents ε.

    def __str__(self) -> str:
        return f"{self.head} → {' '.join(self.body) if self.body else EPSILON}"


class Grammar:
    def __init__(self, productions: list[Production]) -> None:
        if not productions:
            raise ValueError("The grammar has no productions")
        self.productions = productions
        self.start = productions[0].head
        self.nonterminals: list[str] = []
        for p in productions:
            if p.head not in self.nonterminals:
                self.nonterminals.append(p.head)
        self.terminals: list[str] = []
        for p in productions:
            for symbol in p.body:
                if symbol not in self.nonterminals and symbol not in self.terminals:
                    self.terminals.append(symbol)
        self.first = self._compute_first()
        self.follow = self._compute_follow()

    @classmethod
    def load(cls, path: Path = GRAMMAR_PATH) -> "Grammar":
        productions = []
        for raw in Path(path).read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            head, arrow, rest = line.partition("->")
            if not arrow:
                raise ValueError(f"Production is missing '->': {raw}")
            symbols = rest.split()

            if EPSILON in symbols and symbols != [EPSILON]:
                raise ValueError(f"ε must appear alone in a production body: {raw}")

            body = () if symbols == [EPSILON] else tuple(symbols)
            productions.append(Production(len(productions) + 1, head.strip(), body))
        return cls(productions)

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals

    def productions_of(self, head: str) -> list[Production]:
        return [p for p in self.productions if p.head == head]

    def first_of_sequence(self, symbols: tuple[str, ...]) -> set[str]:
        """Return FIRST for X1 X2 ... Xn, including ε if the entire sequence can derive ε."""
        result: set[str] = set()
        for symbol in symbols:
            if not self.is_nonterminal(symbol):
                result.add(symbol)
                return result
            result |= self.first[symbol] - {EPSILON}
            if EPSILON not in self.first[symbol]:
                return result
        result.add(EPSILON)
        return result

    def _compute_first(self) -> dict[str, set[str]]:
        # Fixed-point iteration: repeat until no FIRST set changes.
        first: dict[str, set[str]] = {a: set() for a in self.nonterminals}
        self.first = first
        changed = True
        while changed:
            changed = False
            for p in self.productions:
                new = self.first_of_sequence(p.body)
                if not new <= first[p.head]:
                    first[p.head] |= new
                    changed = True
        return first

    def _compute_follow(self) -> dict[str, set[str]]:
        # FOLLOW rules:
        #   0) Add $ to FOLLOW of the start symbol.
        #   1) If a terminal immediately follows A, add it to FOLLOW(A).
        #   2) Add FIRST of the sequence following A, excluding ε, to FOLLOW(A).
        #   3) If A is at the end of the right-hand side, or if the remaining
        #      sequence can derive ε, add FOLLOW of the production head to FOLLOW(A).
        follow: dict[str, set[str]] = {a: set() for a in self.nonterminals}
        follow[self.start].add(END)
        changed = True
        while changed:
            changed = False
            for p in self.productions:
                for i, symbol in enumerate(p.body):
                    if not self.is_nonterminal(symbol):
                        continue
                    rest = self.first_of_sequence(p.body[i + 1:])
                    new = rest - {EPSILON}
                    if EPSILON in rest:
                        new |= follow[p.head]
                    if not new <= follow[symbol]:
                        follow[symbol] |= new
                        changed = True
        return follow
