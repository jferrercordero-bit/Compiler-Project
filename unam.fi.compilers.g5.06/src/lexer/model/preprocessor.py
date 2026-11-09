"""Normaliza la entrada antes de escanear, sin mover líneas ni columnas."""

# Cada reemplazo es de un carácter por otro, así que las posiciones no cambian.
_REPLACEMENTS = str.maketrans({
    "\u201c": '"',  # “ comilla doble de apertura (aparece al copiar del PDF)
    "\u201d": '"',  # ” comilla doble de cierre
    "\u2018": "'",  # ‘ comilla simple de apertura
    "\u2019": "'",  # ’ comilla simple de cierre
})


class Preprocessor:
    def normalize(self, text: str) -> str:
        return text.translate(_REPLACEMENTS)
