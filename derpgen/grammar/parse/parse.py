from .parser import *
from ..tokenize import Token

from typing import List


__all__ = ['parse_tokens']


def parse_tokens(tokens: List[Token]) -> ParsedGrammar:
    parser = Parser(tokens)
    return parser.parse()


"""
from derpgen.grammar.tokenize import *
from derpgen.grammar.parse import *
from derpgen.grammar.check import *
tokens = tokenize_file('tests/minpy.grammar')
grammar = parse_tokens(tokens)
check_grammar(grammar)

"""
