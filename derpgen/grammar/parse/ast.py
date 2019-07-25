from dataclasses import dataclass
from typing import List


@dataclass
class AST:
    pass


class Production(AST):
    ...


@dataclass
class Rule(AST):
    name: str
    productions: List[Production]
