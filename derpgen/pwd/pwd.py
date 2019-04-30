from .fixed_points import *
from .grammar import *
from .lazy import *
from .match import *
from .memoize import *
from .tree import *

from typing import Callable, List, TypeVar


__all__ = ['is_empty', 'is_nullable', 'parse_null', 'derive', 'make_compact', 'parse', 'parse_compact']


Value = TypeVar('Value')


is_empty: Callable[[Grammar], bool] = fix(lambda: False, EqType.Eq)(match({
    Nil: True,
    Eps: False,
    Tok: False,
    Rep: False,
    Alt: lambda g1, g2: is_empty(g1) and is_empty(g2),
    Seq: lambda g1, g2: is_empty(g1) or is_empty(g2),
    Red: lambda g: is_empty(g),
}))


is_nullable: Callable[[Grammar], bool] = fix(lambda: True, EqType.Eq)(match({
    Nil: False,
    Eps: True,
    Tok: False,
    Rep: lambda g: is_nullable(g) or is_empty(g),
    Alt: lambda g1, g2: is_nullable(g1) or is_nullable(g2),
    Seq: lambda g1, g2: is_nullable(g1) and is_nullable(g2),
    Red: lambda g: is_nullable(g),
}))


parse_null: Callable[[Grammar], List[Tree[Value]]] = fix(list, EqType.Eq)(match({
    Nil: lambda: [],
    Eps: lambda ts: ts,
    Tok: lambda: [],
    Rep: lambda: [Empty()],
    Alt: lambda g1, g2: parse_null(g1) + parse_null(g2),
    Seq: lambda g1, g2: [Branch(t1, t2) for t1 in parse_null(g1) for t2 in parse_null(g2)],
    Red: lambda g, f: [f(t) for t in parse_null(g)],
}))


def derive_seq(c: Value, g1: Grammar, g2: Grammar) -> Grammar:
    dcl_r = delay(lambda: Seq(derive(c, g1), g2))
    if is_nullable(g1):
        return Alt(force(dcl_r),  Seq(Eps(parse_null(g1)), derive(c, g2)))
    else:
        return force(dcl_r)


derive: Callable[[Value, Grammar], Grammar] = memoize(EqType.Equal, EqType.Eq)(match({
    Nil: lambda: Nil(),
    Eps: lambda: Nil(),
    Tok: lambda c, t: Eps([Leaf(c)]) if c == t else Nil(),
    Rep: lambda c, g, g_: Seq(derive(c, g), g_),
    Alt: lambda c, g1, g2: Alt(derive(c, g1), derive(c, g2)),
    Seq: derive_seq,
    Red: lambda c, g, f: Red(derive(c, g), f),
}, ('c', 'g_')))


nullp_t: Tree[Value]


def nullp(g: Grammar) -> bool:
    global nullp_t
    if is_nullable(g):
        ts = parse_null(g)
        if len(ts) == 1:
            nullp_t = ts[0]
            return True
    return False


make_compact: Callable[[Grammar], Grammar] = memoize(EqType.Eq)(match_pred({
    Nil: {lambda: True:                                 lambda g_: g_},
    Eps: {lambda: True:                                 lambda g_: g_},
    Tok: {lambda g_: is_empty(g_):                      lambda: Nil(),
          lambda: True:                                 lambda g_: g_},
    Rep: {lambda g: is_empty(g):                        lambda: Eps([Empty()]),
          lambda: True:                                 lambda g: Rep(make_compact(g))},
    Alt: {lambda g1: is_empty(g1):                      lambda g2: make_compact(g2),
          lambda g2: is_empty(g2):                      lambda g1: make_compact(g1),
          lambda: True:                                 lambda g1, g2: Alt(make_compact(g1), make_compact(g2))},
    Seq: {lambda g1, g2: is_empty(g1) or is_empty(g2):  lambda: Nil(),
          lambda g1: nullp(g1):                         lambda g2: Red(make_compact(g2), lambda w2: Branch(nullp_t, w2)),
          lambda g2: nullp(g2):                         lambda g1: Red(make_compact(g1), lambda w1: Branch(w1, nullp_t)),
          lambda: True:                                 lambda g1, g2: Seq(make_compact(g1), make_compact(g2))},
    Red: {lambda g: g.__class__ is Eps:                 lambda g, f: Eps([f(t) for t in g.ts]),
          lambda g: g.__class__ is Seq and nullp(g.g1): lambda f, g: Red(make_compact(g.g2), lambda t: f(Branch(nullp_t, t))),
          lambda g: g.__class__ is Red:                 lambda g, f: Red(make_compact(g.g), lambda t: g.f(t)),
          lambda: True:                                 lambda g, f: Red(make_compact(g), f)},
}, ('g_',)))


def parse(values: List[Value], g: Grammar) -> List[Tree[Value]]:
    if not values:
        return parse_null(g)
    return parse(values[1:], derive(values[0], g))


def parse_compact(values: List[Value], g: Grammar) -> List[Tree[Value]]:
    if not values:
        return parse_null(g)
    return parse_compact(values[1:], make_compact(derive(values[0], g)))
