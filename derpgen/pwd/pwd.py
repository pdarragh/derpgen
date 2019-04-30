from .fixed_points import *
from .grammar import *
from .match import *
from .memoize import *
from .tree import *

from typing import List, TypeVar


Value = TypeVar('Value')


_is_empty = match({
    Nil: True,
    Eps: False,
    Tok: False,
    Rep: False,
    Alt: lambda g1, g2: is_empty(g1) and is_empty(g2),
    Seq: lambda g1, g2: is_empty(g1) or is_empty(g2),
    Red: lambda g: is_empty(g),
})


@fix(False, EqType.Eq)
def is_empty(g: Grammar) -> bool:
    return _is_empty(g)


@fix(True, EqType.Eq)
def is_nullable(g: Grammar) -> bool:
    pass


@fix([], EqType.Eq)  # TODO: Bottom probably needs to be specified as a function, or else the list will break.
def parse_null(g: Grammar) -> List[Tree[Value]]:
    pass


@memoize(EqType.Equal, EqType.Eq)
def derive(c: Value, g: Grammar) -> Grammar:
    pass


@memoize(EqType.Eq)
def make_compact(g: Grammar) -> Grammar:
    pass


def parse(values: List[Value], g: Grammar) -> List[Tree[Value]]:
    pass


def parse_compact(values: List[Value], g: Grammar) -> List[Tree[Value]]:
    pass
