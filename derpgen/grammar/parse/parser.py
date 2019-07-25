from .ast import *
from ..tokenize import *

from typing import Dict, List


__all__ = ['Parser']


class Parser:
    def __init__(self, tokens: List[Token]):
        # The parser ignores whitespace.
        self.tokens = list(filter(lambda t: t.type not in TokenTypeClasses.WHITESPACE, tokens))
        if not self.tokens:
            raise ValueError  # TODO
        self.index = 0
        self.ast = None
        self.SECTION_DISPATCH = {
            'rules':    self.parse_rules,
            'tokens':   self.parse_tokens,
            'start':    self.parse_start,
        }

    @property
    def token(self):
        return self.tokens[self.index]

    def advance(self):
        self.index += 1

    def parse(self) -> AST:
        ...

    def parse_section(self):
        if self.token.type is not TokenTypes.MODULO:
            raise RuntimeError  # TODO
        self.advance()
        if self.token.type not in TokenTypeClasses.CASES:
            raise RuntimeError  # TODO
        section = self.token.value.lower()
        self.advance()
        if self.token.type is not TokenTypes.MODULO:
            raise RuntimeError  # TODO
        if section not in self.SECTION_DISPATCH:
            raise RuntimeError  # TODO
        self.advance()
        self.SECTION_DISPATCH[section]()

    def parse_rules(self) -> Dict[str, Rule]:
        rules = {}
        while self.token.type is not TokenTypes.MODULO:
            rule = self.parse_rule()
            rules[rule.name] = rule
        return rules

    def parse_rule(self) -> Rule:
        if self.token.type is not TokenTypes.SNAKE_CASE:
            raise RuntimeError  # TODO
        rule_name = self.token.value
        self.advance()
        productions = []
        while ((len(productions) == 0 and self.token.type is TokenTypes.SUBST)
            or (len(productions)  > 0 and self.token.type is TokenTypes.STICK)):
            production = self.parse_production()
            productions.append(production)
        if not productions:
            raise RuntimeError  # TODO
        return Rule(rule_name, productions)

    def parse_production(self) -> Production:
        ...

    def parse_tokens(self):
        ...

    def parse_start(self):
        ...
