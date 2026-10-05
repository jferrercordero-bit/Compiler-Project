"""Assigns a TokenType to a lexeme based on the final state of the DFA."""

from .token_type import TokenType

# Lookup table: maps lexemes that end in q1 to their corresponding token types.
LOOKUP = {
    "int": TokenType.INT, "float": TokenType.FLOAT, "char": TokenType.CHAR, "double": TokenType.DOUBLE,
    "void": TokenType.VOID, "return": TokenType.RETURN, "if": TokenType.IF, "else": TokenType.ELSE,
    "while": TokenType.WHILE, "for": TokenType.FOR, "print": TokenType.PRINT,
    "true": TokenType.TRUE, "false": TokenType.FALSE
}

OPERATORS = {
    "+": TokenType.PLUS, "-": TokenType.MINUS, "*": TokenType.STAR, "/": TokenType.SLASH, "%": TokenType.PERCENT,
    "=": TokenType.ASSIGN, "==": TokenType.EQ, "!": TokenType.NOT, "!=": TokenType.NEQ,
    "<": TokenType.LT, "<=": TokenType.LE, ">": TokenType.GT, ">=": TokenType.GE,
    "&": TokenType.AMP, "&&": TokenType.AND, "|": TokenType.BAR, "||": TokenType.OR
}

PUNCTUATION = {
    "(": TokenType.LPAREN, ")": TokenType.RPAREN, "{": TokenType.LBRACE, "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET, "]": TokenType.RBRACKET, ";": TokenType.SEMI, ",": TokenType.COMMA
}

SPECIALS = {"#": TokenType.HASH, ".": TokenType.DOT}

# Final states that correspond to lexemes that should be discarded (not returned as tokens).
DISCARDED_STATES = {"q9", "q18", "q19"}

_OPERATOR_STATES = {"q7", "q8", "q12", "q13", "q14", "q15"}
_FIXED = {"q2": TokenType.INT_CONST, "q4": TokenType.FLOAT_CONST, 
          "q24": TokenType.CHAR_CONST, "q6": TokenType.STRING
}


class TokenClassifier:
    def classify(self, final_state: str, lexeme: str) -> TokenType | None:
        """Returns the TokenType, or None if the lexeme is discarded."""
        if final_state in DISCARDED_STATES:
            return None
        if final_state == "q1":
            # Priority rule 2: the lookup table takes precedence over identifiers.
            return LOOKUP.get(lexeme, TokenType.ID)
        if final_state in _FIXED:
            return _FIXED[final_state]
        if final_state in _OPERATOR_STATES:
            return OPERATORS[lexeme]
        if final_state == "q16":
            return PUNCTUATION[lexeme]
        if final_state == "q17":
            return SPECIALS[lexeme]
        raise ValueError(f"{final_state} is not a valid final state for lexeme '{lexeme}'")
