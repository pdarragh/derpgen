from .parse import *
from .tokenize import *
from .check import *


__all__ = ['build_grammar_from_file', 'ParsedGrammar']


def build_grammar_from_file(grammar_file: str) -> ParsedGrammar:
    tokens = tokenize_file(grammar_file)
    grammar = parse_tokens(tokens)
    check_grammar(grammar)
    return grammar
