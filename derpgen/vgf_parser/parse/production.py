from .production_part import *

from dataclasses import dataclass
from typing import List


__all__ = ['Production', 'RuleAliasProduction', 'NamedProduction']


@dataclass
class Production:
    pass


@dataclass
class RuleAliasProduction(Production):
    rule: RuleNamePart


@dataclass
class NamedProduction(Production):
    name: ProductionNamePart
    parts: List[ProductionPart]
