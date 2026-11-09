"""SDT types sistem."""

INT, FLOAT, CHAR, ERROR = "int", "float", "char", "error"
NUMERIC = frozenset({INT, FLOAT})
WIDTH = {INT: 4, FLOAT: 4, CHAR: 1}   # bytes for relative address
CONSTANT_TYPE = {"num": INT, "real": FLOAT, "chr": CHAR}


def arithmetic(op: str, left: str, right: str) -> tuple[str, str | None]:
    """Type result from left op right. Raises an error if invalid operation

    """
    if ERROR in (left, right):
        return ERROR, None
    if op == "%":
        if left == INT and right == INT:
            return INT, None
        return ERROR, f"operator '%' needs int operands, found {left} and {right}"
    if left in NUMERIC and right in NUMERIC:
        return (FLOAT if FLOAT in (left, right) else INT), None
    return ERROR, f"operator '{op}' needs numeric operands, found {left} and {right}"


def negate(operand: str) -> tuple[str, str | None]:
    if operand == ERROR:
        return ERROR, None
    if operand in NUMERIC:
        return operand, None
    return ERROR, f"unary '-' needs a numeric operand, found {operand}"


def assignable(target: str, source: str) -> bool:
    """Same type or int to float."""
    return target == source or (target == FLOAT and source == INT)
