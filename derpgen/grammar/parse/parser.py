from .ast import *
from ..tokenize import *

from typing import Dict, List, Optional


__all__ = ['Parser']


class Parser:
    def __init__(self, tokens: List[Token]):
        # The parser ignores whitespace.
        self.tokens = list(filter(lambda t: t.type not in TokenTypeClasses.WHITESPACE and
                                            t.type not in TokenTypeClasses.COMMENTS,
                                  tokens))
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
    def token(self) -> Token:
        return self.tokens[self.index]

    @property
    def next_token(self) -> Optional[Token]:
        if self.index + 1 >= len(self.tokens):
            return None
        return self.tokens[self.index + 1]

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
        if self.token.type is TokenTypes.PASCAL_CASE:
            return self.parse_named_production()
        elif self.token.type is TokenTypes.SNAKE_CASE:
            return self.parse_alias_production()
        else:
            raise RuntimeError  # TODO

    def parse_named_production(self) -> NamedProduction:
        name = self.token.value
        self.advance()
        parts = []
        # Keep parsing for parts until either we reach the end of the tokens or the lookahead token indicates we're done
        # with this production.
        while self.tokens:
            if self.next_token is not None and self.next_token.type in TokenTypeClasses.DIVIDERS:
                break
            part = self.parse_part()
            parts.append(part)
        if not parts:
            raise RuntimeError  # TODO
        return NamedProduction(name, parts)

    def parse_part(self) -> Part:
        if self.token.type in TokenTypeClasses.GROUPS:
            return self.parse_group()
        elif self.token.type is TokenTypes.SNAKE_CASE:
            ...
        else:
            raise RuntimeError  # TODO

    def parse_group(self) -> ...:
        if self.token.type is TokenTypes.L_PAR:
            group_type = GroupType.PLAIN
        elif self.token.type is TokenTypes.L_BRK:
            group_type = GroupType.OPTIONAL
        elif self.token.type is TokenTypes.L_BRC:
            group_type = GroupType.REPETITION
        elif self.token.type is TokenTypes.L_ABR:
            group_type = GroupType.NONEMPTY_REPETITION
        else:
            raise RuntimeError  # TODO
        expected_end_token_type = BRACE_PAIRS[self.token.type]
        self.advance()
        parts = []
        while self.token.type is not expected_end_token_type:
            part = self.parse_part()
            parts.append(part)
        if not parts:
            raise RuntimeError  # TODO
        return Group(group_type, parts)

    def parse_alias_production(self) -> AliasProduction:
        alias = self.token.value
        self.advance()
        return AliasProduction(alias)

    def parse_tokens(self):
        ...

    def parse_start(self):
        ...
