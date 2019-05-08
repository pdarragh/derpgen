from .pwd import *
from .transformers import (
    optional_t                  as opt,
    list_t                      as lst,
    nonempty_list_t             as min_lst,
    separated_list_t            as sep_lst,
    nonempty_separated_list_t   as min_sep_lst
)
from .vgf_parser import *

from derpgen.utility.match import *
from typing import Callable, List, NamedTuple, Optional, TypeVar


Value = TypeVar('Value')
PartTuple = NamedTuple('PartTuple', [('g', Grammar), ('name', Optional[str])])


def generate_grammar_from_file(vgf_file: str) -> GrammarDict:
    parsed_rules = parse_grammar_file(vgf_file)
    rule_dict = {}
    for rule_name, productions in parsed_rules.items():
        g = process_rule(productions, rule_dict)
        rule_dict[rule_name] = g
    return rule_dict


def process_rule(productions: List[Production], rule_dict: GrammarDict) -> Grammar:
    gs = []
    for production in productions:
        g = process_production(production, rule_dict)
        gs.append(g)
    return alt(*gs)


def process_rule_alias_production(production: RuleAliasProduction, rule_dict: GrammarDict) -> Grammar:
    return ref(production.rule.token.text, rule_dict)


def process_named_production(production: NamedProduction, rule_dict: GrammarDict) -> Grammar:
    parameters: List[Optional[str]] = []
    gs = []
    for part in production.parts:
        g = process_production_part(part, rule_dict)
        gs.append(g.g)
        parameters.append(g.name)
    g = seq(*gs)
    return g


process_production: Callable[[Production, GrammarDict], Grammar] = match({
    RuleAliasProduction:    process_rule_alias_production,
    NamedProduction:        process_named_production,
}, Production, ('production', 'rule_dict'), destructure=False)


process_production_part: Callable[[ProductionPart, GrammarDict], PartTuple] = match({
    LiteralPart:                lambda part, rule_dict: PartTuple(tok(part.token.text), None),
    SpecialPart:                lambda part, rule_dict: PartTuple(tok(part.token.text), None),
    RuleNamePart:               lambda part, rule_dict: PartTuple(ref(part.token.text, rule_dict), None),
    ActualPart:                 lambda part, rule_dict: PartTuple(tok(part.token.text), None),

    OptionalPart:               lambda part, rule_dict: PartTuple(opt(process_production_part(part.actual,
                                                                                              rule_dict).g), None),
    ListPart:                   lambda part, rule_dict: PartTuple(lst(process_production_part(part.actual,
                                                                                              rule_dict).g), None),
    NonemptyListPart:           lambda part, rule_dict: PartTuple(min_lst(process_production_part(part.actual,
                                                                                                  rule_dict).g), None),
    SeparatedListPart:          lambda part, rule_dict: PartTuple(sep_lst(process_production_part(part.separator,
                                                                                                  rule_dict).g,
                                                                          process_production_part(part.actual,
                                                                                                  rule_dict).g), None),
    NonemptySeparatedListPart:  lambda part, rule_dict: PartTuple(min_sep_lst(process_production_part(part.separator,
                                                                                                      rule_dict).g,
                                                                              process_production_part(part.actual,
                                                                                                      rule_dict).g),
                                                                  None),

    ParameterPart:              lambda part, rule_dict: PartTuple(process_production_part(part.part, rule_dict).g,
                                                                  part.name),
}, ProductionPart, ('part', 'rule_dict'), destructure=False, omit={ProductionNamePart, ModifiedPart, SeparatedPart})
