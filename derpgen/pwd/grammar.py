from .tree import Tree

from derpgen.utility import has_class

from dataclasses import dataclass
from typing import Callable, Generic, List, TypeVar


__all__ = ['Grammar',
           'Nil', 'Eps', 'Tok', 'Rep', 'Alt', 'Seq', 'Red',
           'nil', 'eps', 'tok', 'rep', 'alt', 'seq', 'red']


Value = TypeVar('Value')
RedFunc = Callable[[Tree[Value]], Tree[Value]]


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
    f: RedFunc


########
# Convenience functions.
########


def unit(x) -> Grammar:
    if not isinstance(x, Grammar):
        return tok(x)
    return x


def nil() -> Grammar:
    return Nil()


def eps(ts: List[Tree[Value]]) -> Grammar:
    return Eps(ts)


def tok(t: Value) -> Grammar:
    return Tok(t)


def rep(g: Grammar) -> Grammar:
    if has_class(g, Rep):
        return g
    return Rep(unit(g))


def alt(*gs: Grammar) -> Grammar:
    if not gs:
        raise RuntimeError("No arguments given in call to alt.")
    if len(gs) == 1:
        return unit(gs[0])
    res = Alt(unit(gs[-2]), unit(gs[-1]))
    for g in reversed(gs[:-2]):
        res = Alt(unit(g), res)
    return res


def seq(*gs: Grammar) -> Grammar:
    if not gs:
        raise RuntimeError("No arguments given in call to seq.")
    if len(gs) == 1:
        return unit(gs[0])
    res = Seq(unit(gs[-2]), unit(gs[-1]))
    for g in reversed(gs[:-2]):
        res = Seq(unit(g), res)
    return res


def red(g: Grammar, f: RedFunc) -> Grammar:
    return Red(unit(g), f)
