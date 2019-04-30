from .fixed_points import *
from .grammar import *
from .memoize import *
from .tree import *

from typing import List, TypeVar


Value = TypeVar('Value')


@fix(False, EqType.Eq)
def is_empty(g: Grammar) -> bool:
    pass


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
