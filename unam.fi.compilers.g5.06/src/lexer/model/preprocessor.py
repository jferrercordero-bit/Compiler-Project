"""Normalizes the input before scanning, without changing lines or columns positions."""

# Each replacement maps one character to another, so positions do not change.
_REPLACEMENTS = str.maketrans({
    "\u201c": '"',  # “ left double quotation mark (may appear when copying text from the PDF)
    "\u201d": '"',  # ” right double quotation mark
    "\u2018": "'",  # ‘ left single quotation mark (may appear when copying text from the PDF)
    "\u2019": "'",  # ’ right single quotation mark
})


class Preprocessor:
    def normalize(self, text: str) -> str:
        return text.translate(_REPLACEMENTS)
