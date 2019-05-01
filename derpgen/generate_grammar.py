from .pwd import *
from .vgf_parser import *

from .transformers import (
    optional_t as opt,
    list_t as lst,
    nonempty_list_t as min_lst,
    separated_list_t as sep_lst,
    nonempty_separated_list_t as min_sep_lst
)

from derpgen.utility.match import *

from dataclasses import dataclass
from typing import Callable, Dict, List, NamedTuple, Optional, TypeVar


Value = TypeVar('Value')
RuleDict = Dict[str, Grammar]
PartTuple = NamedTuple('PartTuple', [('g', Grammar), ('name', str)])


@dataclass
class RuleLit(Grammar[Value]):
    name: str
    rule_dict: RuleDict


def generate_grammar_from_file(vgf_file: str) -> RuleDict:
    parsed_rules = parse_grammar_file(vgf_file)
    rule_dict = {}
    for rule_name, productions in parsed_rules.items():
        g = process_rule(productions, rule_dict)
        rule_dict[rule_name] = g
    return rule_dict


def process_rule(productions: List[Production], rule_dict: RuleDict) -> Grammar:
    gs = []
    for production in productions:
        g = process_production(production, rule_dict)
        gs.append(g)
    return alt(*gs)


def process_rule_alias_production(production: RuleAliasProduction, rule_dict: RuleDict) -> Grammar:
    return RuleLit(production.rule.token.text, rule_dict)


def process_named_production(production: NamedProduction, rule_dict: RuleDict) -> Grammar:
    parameters: List[Optional[str]] = []
    gs = []
    for part in production.parts:
        g = process_production_part(part, rule_dict)
        gs.append(g.g)
        parameters.append(g.name)
    g = seq(*gs)
    return g


process_production: Callable[[Production, RuleDict], Grammar] = match({
    RuleAliasProduction:    process_rule_alias_production,
    NamedProduction:        process_named_production,
}, ('production', 'rule_dict'))


process_production_part: Callable[[ProductionPart, RuleDict], PartTuple] = match({
    LiteralPart:                lambda part:            PartTuple(tok(part.token.text), None),
    SpecialPart:                lambda part:            PartTuple(tok(part.token.text), None),
    RuleNamePart:               lambda part, rule_dict: PartTuple(RuleLit(part.token.text, rule_dict), None),
    ActualPart:                 lambda part:            PartTuple(tok(part.token.text), None),

    OptionalPart:               lambda part, rule_dict: PartTuple(opt(process_production_part(part.actual, rule_dict)), None),
    ListPart:                   lambda part, rule_dict: PartTuple(lst(process_production_part(part.actual, rule_dict)), None),
    NonemptyListPart:           lambda part, rule_dict: PartTuple(min_lst(process_production_part(part.actual, rule_dict)), None),
    SeparatedListPart:          lambda part, rule_dict: PartTuple(sep_lst(process_production_part(part.separator, rule_dict), process_production_part(part.actual, rule_dict)), None),
    NonemptySeparatedListPart:  lambda part, rule_dict: PartTuple(min_sep_lst(process_production_part(part.separator, rule_dict), process_production_part(part.actual, rule_dict)), None),

    ParameterPart:              lambda part, rule_dict: PartTuple(process_production_part(part.part, rule_dict), part.name),
}, ('part', 'rule_dict'))
