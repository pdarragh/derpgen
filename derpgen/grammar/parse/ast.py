from dataclasses import dataclass, field
from enum import Enum, auto, unique
from typing import List


@unique
class GroupType(Enum):
    PLAIN           = auto()
    OPTIONAL        = auto()
    REPETITION          = auto()
    NONEMPTY_REPETITION = auto()


@dataclass
class AST:
    pass


@dataclass
class Part(AST):
    ...


@dataclass
class Group(AST):
    type: GroupType
    parts: List[Part]


@dataclass
class Production(AST):
    ...


@dataclass
class NamedProduction(Production):
    name: str
    parts: List[Part]


@dataclass
class AliasProduction(Production):
    alias: str


@dataclass
class Rule(AST):
    name: str
    productions: List[Production]
