"""Symbol table implementation with lookup and insert operations."""

from dataclasses import dataclass, field


@dataclass
class SymbolEntry:
    # The lexer only knows the name and lines; the remaining fields are filled in during later phases..
    name: str
    type: str = "TBD"
    size: str = "TBD"
    dimension: str = "TBD"
    lines: list[int] = field(default_factory=list)
    address: str = "TBD"


class SymbolTable:
    def __init__(self) -> None:
        self._entries: dict[str, SymbolEntry] = {}

    def lookup(self, name: str) -> SymbolEntry | None:
        return self._entries.get(name)

    def insert(self, name: str, line: int) -> SymbolEntry:
        entry = SymbolEntry(name, lines=[line])
        self._entries[name] = entry
        return entry

    def record(self, name: str, line: int) -> SymbolEntry:
        """Looks up an identifier, inserts it if necessary, and records the line where it appears."""
        entry = self.lookup(name)
        if entry is None:
            return self.insert(name, line)
        if line not in entry.lines:
            entry.lines.append(line)
        return entry

    def entries(self) -> list[SymbolEntry]:
        return list(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)
