from typing import Callable, Iterable, Reversible, TypeVar

import functools


__all__ = ['concat', 'cons', 'foldl', 'foldr', 'list_product', 'partial']


A = TypeVar('A')
B = TypeVar('B')


def concat(xss: Iterable[Iterable[A]]) -> Iterable[A]:
    # Pronunciation guide:
    #   xs = "exes", i.e., plural of x ("ex")
    #   xss = "exeses", i.e., plural of xs
    return [x for xs in xss for x in xs]


def cons(x: A, xs: Iterable[A]) -> Iterable[A]:
    return [x] + xs


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


def list_product(xs: Iterable[A], yss: Iterable[Iterable[A]]) -> Iterable[Iterable[A]]:
    return concat(map(lambda l: map(partial(cons, l), yss), xs))


partial = functools.partial

