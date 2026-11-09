"""Tabla de símbolos con las operaciones insert() y lookup() vistas en clase."""

from dataclasses import dataclass, field


@dataclass
class SymbolEntry:
    # El lexer solo conoce el nombre y las líneas; el resto lo llenan fases posteriores.
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
        """Busca el identificador; si no existe lo inserta, si existe agrega la línea."""
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
