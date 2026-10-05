"""Transition table for the 25-state DFA used by the lexical analyzer."""

from pathlib import Path

from .char_class import CLASSES

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "transition_table.csv"

START = "q0"

# Final states (section 5.3). q0, q3, q5, q10, q11 and q20 through q23 are not final.
FINAL_STATES = {
    "q1", "q2", "q4", "q6", "q7", "q8", "q9", "q12", "q13",
    "q14", "q15", "q16", "q17", "q18", "q19", "q24"
}


class TransitionTable:
    """Transition function δ(state, class). A dash in the CSV means no transition."""

    def __init__(self, path: Path = CSV_PATH) -> None:
        self._delta: dict[str, dict[str, str | None]] = {}
        rows = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
        if not rows:
            raise ValueError("The transition table is empty.")
        header = rows[0].split(",")
        if tuple(header[1:]) != CLASSES:
            raise ValueError("The CSV header does not match the expected character classes.")
        for row in rows[1:]:
            cells = row.split(",")
            if len(cells) != len(header):
                raise ValueError(f"Malformed row in the transition table: {row}")
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
