from .grammar import *
from .transformers import (
    optional_t                  as opt,
    list_t                      as lst,
    nonempty_list_t             as min_lst,
    separated_list_t            as sep_lst,
    nonempty_separated_list_t   as min_sep_lst
)

from derpgen.utility.match import *
from derpgen.vgf_parser import *

from typing import Callable, List, NamedTuple, Optional, TypeVar

import re


__all__ = ['generate_grammar_from_file']


Value = TypeVar('Value')
PartTuple = NamedTuple('PartTuple', [('g', Grammar), ('name', Optional[str])])


def generate_grammar_from_file(vgf_file: str) -> Grammar:
    parsed_sections = parse_grammar_file(vgf_file)
    grammar_dict: GrammarDict = {}
    for rule_name, productions in parsed_sections.grammar_parse.items():
        g = process_rule(productions, grammar_dict, parsed_sections.tokens_parse)
        grammar_dict[rule_name] = g
    generated_grammar = alt(*(grammar_dict[s] for s in parsed_sections.start_symbols))
    return generated_grammar


def process_rule(productions: List[Production], rule_dict: GrammarDict, token_definitions: RegexDict) -> Grammar:
    gs = []
    for production in productions:
        g = process_production(production, rule_dict, token_definitions)
        gs.append(g)
    return alt(*gs)


def process_rule_alias_production(production: RuleAliasProduction, rule_dict: GrammarDict) -> Grammar:
    return ref(production.rule.token.text, rule_dict)


def process_named_production(production: NamedProduction, rule_dict: GrammarDict,
                             token_definitions: RegexDict) -> Grammar:
    parameters: List[Optional[str]] = []
    gs = []
    for part in production.parts:
        g = process_production_part(part, rule_dict, token_definitions)
        gs.append(g.g)
        parameters.append(g.name)
    g = seq(*gs)
    return g


process_production: Callable[[Production, GrammarDict], Grammar] = match({
    RuleAliasProduction: lambda production, rule_dict, _: process_rule_alias_production(production, rule_dict),
    NamedProduction:     process_named_production,
}, Production, ('production', 'rule_dict', 'token_definitions'), destructure=False)


def process_special_part(part: SpecialPart, token_definitions: RegexDict) -> PartTuple:
    pat_name = part.token.text
    pattern = token_definitions[pat_name]  # derpgen.vgf_parser.parse ensures all patterns exist.
    return PartTuple(pat(re.compile(pattern)), None)


process_production_part: Callable[[ProductionPart, GrammarDict], PartTuple] = match({
    LiteralPart:               lambda part, rule_dict, _: PartTuple(tok(part.token.text), None),
    SpecialPart:               lambda part, _, tok_defs:  process_special_part(part, tok_defs),
    RuleNamePart:              lambda part, rule_dict, _: PartTuple(ref(part.token.text, rule_dict), None),
    ActualPart:                lambda part, rule_dict, _: PartTuple(tok(part.token.text), None),

    OptionalPart:
        lambda part, rule_dict, tok_defs:
        PartTuple(opt(process_production_part(part.actual, rule_dict, tok_defs).g), None),
    ListPart:
        lambda part, rule_dict, tok_defs:
        PartTuple(lst(process_production_part(part.actual, rule_dict, tok_defs).g), None),
    NonemptyListPart:
        lambda part, rule_dict, tok_defs:
        PartTuple(min_lst(process_production_part(part.actual, rule_dict, tok_defs).g), None),
    SeparatedListPart:
        lambda part, rule_dict, tok_defs:
        PartTuple(sep_lst(process_production_part(part.separator, rule_dict, tok_defs).g,
                          process_production_part(part.actual, rule_dict, tok_defs).g), None),
    NonemptySeparatedListPart:
        lambda part, rule_dict, tok_defs:
        PartTuple(min_sep_lst(process_production_part(part.separator, rule_dict, tok_defs).g,
                              process_production_part(part.actual, rule_dict, tok_defs).g), None),

    ParameterPart:
        lambda part, rule_dict, tok_defs:
        PartTuple(process_production_part(part.part, rule_dict, tok_defs).g, part.name),
}, ProductionPart, ('part', 'rule_dict', 'tok_defs'), destructure=False,
    omit={ProductionNamePart, ModifiedPart, SeparatedPart})
