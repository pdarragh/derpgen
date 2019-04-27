from ..tokenize import *

from dataclasses import dataclass


__all__ = [
    'ProductionPart',
    'ActualPart', 'LiteralPart', 'SpecialPart', 'RuleNamePart', 'ProductionNamePart',
    'ModifiedPart', 'OptionalPart', 'ListPart', 'NonemptyListPart',
    'SeparatedPart', 'SeparatedListPart', 'NonemptySeparatedListPart',
    'ParameterPart',
]


@dataclass
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
class ProductionNamePart(ActualPart):
    token: CapitalWordToken


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
    part: ProductionPart
