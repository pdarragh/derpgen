from .parser import *
from ..tokenize import Token

from typing import List


__all__ = ['parse_tokens']


def parse_tokens(tokens: List[Token]) -> ParsedGrammar:
    parser = Parser(tokens)
    return parser.parse()
