from typing import Callable, Iterable, Reversible, TypeVar


__all__ = ['foldl', 'foldr']


A = TypeVar('A')
B = TypeVar('B')


def foldl(f: Callable[[B, A], B], init: B, xs: Iterable[A]) -> B:
    prev = init
    for x in xs:
        prev = f(prev, x)
    return prev


def foldr(f: Callable[[A, B], B], init: B, xs: Reversible[A]) -> B:
    prev = init
    for x in reversed(xs):
        prev = f(x, prev)
    return prev
