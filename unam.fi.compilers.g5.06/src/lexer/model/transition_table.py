"""El AFD de 25 estados, cargado tal cual desde data/transition_table.csv."""

from pathlib import Path

from .char_class import CLASSES

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "transition_table.csv"

START = "q0"

# Estados finales (sección 5.3). q0, q3, q5, q10, q11 y q20 a q23 no son finales.
FINAL_STATES = frozenset({
    "q1", "q2", "q4", "q6", "q7", "q8", "q9", "q12", "q13",
    "q14", "q15", "q16", "q17", "q18", "q19", "q24",
})


class TransitionTable:
    """Función de transición δ(estado, clase). Un guion en el CSV es "sin movimiento"."""

    def __init__(self, path: Path = CSV_PATH) -> None:
        self._delta: dict[str, dict[str, str | None]] = {}
        rows = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
        header = rows[0].split(",")
        if tuple(header[1:]) != CLASSES:
            raise ValueError("Las columnas del CSV no coinciden con las 18 clases de caracteres")
        for row in rows[1:]:
            cells = row.split(",")
            if len(cells) != len(header):
                raise ValueError(f"Fila mal formada en la tabla de transiciones: {row}")
            state, targets = cells[0], cells[1:]
            self._delta[state] = {
                cls: (None if target == "-" else target) for cls, target in zip(CLASSES, targets)
            }

    def next_state(self, state: str, char_cls: str) -> str | None:
        return self._delta[state][char_cls]

    @staticmethod
    def is_final(state: str) -> bool:
        return state in FINAL_STATES

    @property
    def states(self) -> list[str]:
        return list(self._delta)

    def row(self, state: str) -> dict[str, str | None]:
        return dict(self._delta[state])
