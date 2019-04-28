from .tree import Tree

from dataclasses import dataclass
from typing import Callable, List, TypeVar


__all__ = ['Grammar', 'Nil', 'Eps', 'Tok', 'Rep', 'Alt', 'Seq', 'Red']


V = TypeVar('V')


@dataclass
class Grammar:
    pass


@dataclass
class Nil(Grammar):
    pass


@dataclass
class Eps(Grammar):
    trees: List[Tree[V]]


@dataclass
class Tok(Grammar):
    value: V


@dataclass
class Rep(Grammar):
    grammar: Grammar


@dataclass
class Alt(Grammar):
    this: Grammar
    that: Grammar


@dataclass
class Seq(Grammar):
    left: Grammar
    right: Grammar


@dataclass
class Red(Grammar):
    grammar: Grammar
    function: Callable[[Tree[V]], Tree[V]]
