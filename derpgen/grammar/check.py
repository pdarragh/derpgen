from .parse import *

from typing import Set


__all__ = ['check_grammar']


def check_grammar(grammar: ParsedGrammar):
    production_names = set()
    assumed_tokens = set()
    # Check each rule.
    for tree in grammar.rules.values():
        check_ast(tree, grammar, production_names, assumed_tokens)
    # Check that all declared tokens are used.
    for token in grammar.token_matchers:
        if token not in assumed_tokens:
            raise RuntimeError  # TODO
    # Check that there is a start symbol and that all start symbols exist.
    if not grammar.start_symbols:
        raise RuntimeError  # TODO
    for start_symbol in grammar.start_symbols:
        if start_symbol not in grammar.rules:
            raise RuntimeError  # TODO


def check_ast(tree: AST, grammar: ParsedGrammar, production_names: Set[str], assumed_tokens: Set[str]):
    def _check_ast(_tree: AST):
        if isinstance(_tree, Sequence):
            for sub_ast in _tree.asts:
                _check_ast(sub_ast)
        elif isinstance(_tree, ParameterizedSequence):
            _check_ast(_tree.sequence)
            _check_ast(_tree.parameter)
        elif isinstance(_tree, Literal):
            # Literals are always acceptable as-is.
            pass
        elif isinstance(_tree, DeclaredToken):
            # Declared tokens must be defined in the tokens section.
            if _tree.token not in grammar.token_matchers:
                raise RuntimeError  # TODO
            assumed_tokens.add(_tree.token)
        elif isinstance(_tree, PatternMatch):
            _check_ast(_tree.match)
        elif isinstance(_tree, RuleMatch):
            # Rule matches must refer to existing rules.
            if _tree.rule not in grammar.rules:
                raise RuntimeError  # TODO
        elif isinstance(_tree, NamedProduction):
            # Ensure each production's name is unique.
            if _tree.name in production_names:
                raise RuntimeError  # TODO
            production_names.add(_tree.name)
            for part in _tree.parts:
                _check_ast(part)
        elif isinstance(_tree, AliasProduction):
            # Aliases must correspond to real rules.
            if _tree.alias not in grammar.rules:
                raise RuntimeError  # TODO
        elif isinstance(_tree, Rule):
            for production in _tree.productions:
                _check_ast(production)
        else:
            raise RuntimeError  # TODO
    _check_ast(tree)
