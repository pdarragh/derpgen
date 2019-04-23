from .production_part import *

from dataclasses import dataclass
from typing import List


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
