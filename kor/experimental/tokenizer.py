import re
from typing import List, Tuple, Union, Sequence, Literal
from kor.experimental.s_exprs import (
    SExpr,
    Number,
    String,
    SList,
    Object,
    Function,
    TypeAnnotation,
)


def tokenize(s_expression: str) -> List[Tuple[str, Union[str, float]]]:
    """Tokenize a s-expression into a list of tokens."""
    token_pattern = r"""
        (?P<whitespace>\s+) |
        (?P<number>-?\d+(?:\.\d+)?) |
        (?P<string>"(?:[^\\"]|\\.)*") |
        (?P<symbol>[^\s()\[\]{}'`",;]+) |
        (?P<open_paren>\() |
        (?P<close_paren>\))
    """
    tokens: List[Tuple[str, Union[str, float]]] = []
    scanner = re.finditer(token_pattern, s_expression, re.VERBOSE)

    for match in scanner:
        if match.lastgroup != "whitespace":
            token_value = match.group(match.lastgroup)
            if match.lastgroup == "number":
                token_value = token_value
            tokens.append((match.lastgroup, token_value))

    return tokens


TokenType = Union[
    Literal["open_paren"],
    Literal["close_paren"],
    Literal["number"],
    Literal["string"],
    Literal["symbol"],
]


class Parser:
    def __init__(self, tokens: Sequence[Tuple[TokenType, str]]) -> None:
        """Initialize the parser."""
        self.tokens = tokens
        self.position = 0

    def parse(self):
        return self.parse_sexp()

    def parse_sexp(self):
        if self.position >= len(self.tokens):
            return None

        token_type, token_value = self.tokens[self.position]

        if token_type == "open_paren":
            self.position += 1
            elements = []

            while (
                self.position < len(self.tokens)
                and self.tokens[self.position][0] != "close_paren"
            ):
                elements.append(self.parse_sexp())

            if (
                self.position < len(self.tokens)
                and self.tokens[self.position][0] == "close_paren"
            ):
                self.position += 1
            else:
                raise ValueError("Unbalanced parentheses")

            return SList(elements)
        elif token_type == "number":
            self.position += 1
            return Number(float(token_value))
        elif token_type == "string":
            self.position += 1
            return String(eval(token_value))
        elif token_type == "symbol":
            self.position += 1
            return Function(token_value)

        else:
            raise ValueError(f"Unexpected token: {token_type}, {token_value}")

    def parse_function(self) -> Function:
        if (
            self.position >= len(self.tokens)
            or self.tokens[self.position][0] != "open_paren"
        ):
            raise ValueError("Function parameters expected")
        self.position += 1

        parameters = []
        while (
            self.position < len(self.tokens)
            and self.tokens[self.position][0] != "close_paren"
        ):
            token_type, token_value = self.tokens[self.position]
            if token_type != "symbol":
                raise ValueError("Function parameters must be symbols")
            parameters.append(Symbol(token_value))
            self.position += 1

        if (
            self.position < len(self.tokens)
            and self.tokens[self.position][0] == "close_paren"
        ):
            self.position += 1
        else:
            raise ValueError("Unbalanced parentheses")

        body = self.parse_sexp()

        return Function(parameters, body)


def parse_s_expression(s_expression):
    tokens = tokenize(s_expression)
    parser = Parser(tokens)
    return parser.parse()
