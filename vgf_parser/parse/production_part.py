from vgf_parser.tokenize.vgf_token import *

from dataclasses import dataclass


__all__ = [
    'ProductionPart',
    'ActualPart', 'LiteralPart', 'SpecialPart', 'RuleNamePart',
    'ModifiedPart', 'OptionalPart', 'ListPart', 'NonemptyListPart',
    'SeparatedPart', 'SeparatedListPart', 'NonemptySeparatedListPart',
    'ParameterPart',
]


class ProductionPart:
    pass


@dataclass
class ActualPart(ProductionPart):
    token: VgfToken


@dataclass
class LiteralPart(ActualPart):
    token: StringToken


@dataclass
class SpecialPart(ActualPart):
    token: AllCapitalWordToken


@dataclass
class RuleNamePart(ActualPart):
    token: BracketedTextToken


@dataclass
class ModifiedPart(ProductionPart):
    actual: ActualPart


class OptionalPart(ModifiedPart):
    pass


class ListPart(ModifiedPart):
    pass


class NonemptyListPart(ModifiedPart):
    pass


@dataclass
class SeparatedPart(ModifiedPart):
    separator: BracedTextToken


class SeparatedListPart(SeparatedPart):
    pass


class NonemptySeparatedListPart(SeparatedPart):
    pass


@dataclass
class ParameterPart(ProductionPart):
    name: LowercaseWordToken
    part: ModifiedPart
