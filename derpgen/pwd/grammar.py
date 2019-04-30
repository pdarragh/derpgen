from .tree import Tree

from dataclasses import dataclass
from typing import Callable, List, TypeVar


__all__ = ['Grammar', 'Nil', 'Eps', 'Tok', 'Rep', 'Alt', 'Seq', 'Red']


Value = TypeVar('Value')


@dataclass
class Grammar:
    pass


@dataclass
class Nil(Grammar):
    pass


@dataclass
class Eps(Grammar):
    ts: List[Tree[Value]]


@dataclass
class Tok(Grammar):
    t: Value


@dataclass
class Rep(Grammar):
    g: Grammar


@dataclass
class Alt(Grammar):
    g1: Grammar
    g2: Grammar


@dataclass
class Seq(Grammar):
    g1: Grammar
    g2: Grammar


@dataclass
class Red(Grammar):
    g: Grammar
    f: Callable[[Tree[Value]], Tree[Value]]
