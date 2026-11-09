"""Parse tree nodes and their text representation."""

from dataclasses import dataclass, field

from .grammar import EPSILON, Production
from .token_adapter import InputSymbol

_LEXEME_TERMINALS = {"id", "num", "real", "chr"}


@dataclass(eq=False)
class Node:
    symbol: str
    children: list["Node"] = field(default_factory=list)
    production: Production | None = None   # The production used to expand this nonterminal.
    token: InputSymbol | None = None       # The input token matched by this terminal leaf.
    attrs: dict[str, object] = field(default_factory=dict)

    def label(self) -> str:
        if self.symbol == EPSILON:
            return EPSILON
        text = self.symbol
        if self.token is not None and self.symbol in _LEXEME_TERMINALS:
            text += f": {self.token.lexeme}"
        if self.attrs:
            text += "  [" + ", ".join(f"{k}={v}" for k, v in self.attrs.items()) + "]"
        return text

    def leaves(self) -> list["Node"]:
        """Return leaf nodes from left to right, excluding ε."""
        if not self.children:
            return [] if self.symbol == EPSILON else [self]
        return [leaf for child in self.children for leaf in child.leaves()]

    def render(self) -> str:
        lines = [self.label()]
        self._render_children("", lines)
        return "\n".join(lines)

    def _render_children(self, prefix: str, lines: list[str]) -> None:
        for i, child in enumerate(self.children):
            last = i == len(self.children) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.label())
            child._render_children(prefix + ("    " if last else "│   "), lines)
