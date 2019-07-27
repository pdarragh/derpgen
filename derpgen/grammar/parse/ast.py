from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import List, Union


@unique
class GroupType(Enum):
    PLAIN               = auto()
    OPTIONAL            = auto()
    REPETITION          = auto()
    NONEMPTY_REPETITION = auto()


@dataclass
class AST:
    pass


@dataclass
class SequencedGroup(AST):
    type: GroupType
    parts: List[AST]


@dataclass
class AlternatingGroup(AST):
    type: GroupType
    alternates: List[AST]


Group = Union[SequencedGroup, AlternatingGroup]


@dataclass
class Literal(AST):
    string: str


@dataclass
class DeclaredToken(AST):
    string: str


@dataclass
class PatternMatch(AST):
    name: str
    match: AST


@dataclass
class RuleMatch(AST):
    name: str
    rule: str


Part = Union[Group, Literal, PatternMatch, RuleMatch]


@dataclass
class NamedProduction(AST):
    name: str
    parts: List[Part]


@dataclass
class AliasProduction(AST):
    alias: str


Production = Union[NamedProduction, AliasProduction]


@dataclass
class Rule(AST):
    name: str
    productions: List[Production]
