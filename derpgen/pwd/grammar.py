from .tree import Tree

from dataclasses import dataclass
from typing import Callable, Generic, List, TypeVar


__all__ = ['Grammar', 'Nil', 'Eps', 'Tok', 'Rep', 'Alt', 'Seq', 'Red']


Value = TypeVar('Value')


@dataclass
class Grammar(Generic[Value]):
    pass


@dataclass
class Nil(Grammar[Value]):
    pass


@dataclass
class Eps(Grammar[Value]):
    ts: List[Tree[Value]]


@dataclass
class Tok(Grammar[Value]):
    t: Value


@dataclass
class Rep(Grammar[Value]):
    g: Grammar


@dataclass
class Alt(Grammar[Value]):
    g1: Grammar
    g2: Grammar


@dataclass
class Seq(Grammar[Value]):
    g1: Grammar
    g2: Grammar


@dataclass
class Red(Grammar[Value]):
    g: Grammar
    f: Callable[[Tree[Value]], Tree[Value]]
