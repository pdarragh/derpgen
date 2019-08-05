from typing import Callable, Iterable, Reversible, TypeVar

import functools


__all__ = [
    'concat', 'cons', 'snoc',
    'foldl', 'foldr',
    'binary_cartesian_product', 'cartesian_product', 'list_product',
    'partial'
]


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


def concat(xss: Iterable[Iterable[A]]) -> Iterable[A]:
    # Pronunciation guide:
    #   xs = "exes", i.e., plural of x ("ex")
    #   xss = "exeses", i.e., plural of xs
    return [x for xs in xss for x in xs]


def cons(x: A, xs: Iterable[A]) -> Iterable[A]:
    return [x] + xs


def snoc(xs: Iterable[A], x: A) -> Iterable[A]:
    return list(xs) + [x]


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


def binary_cartesian_product(xs: Iterable[A], ys: Iterable[B], f: Callable[[A, B], C]) -> Iterable[C]:
    if not xs:
        return []
    x, *xs_ = xs
    return list(map(partial(f, x), ys)) + binary_cartesian_product(xs_, ys, f)


def cartesian_product(xss: Iterable[Iterable[A]]) -> Iterable[Iterable[A]]:
    if not xss:
        return [[]]
    xs, *xss_ = xss
    products = cartesian_product(xss_)
    return binary_cartesian_product(xs, products, cons)


def list_product(xs: Iterable[A], yss: Iterable[Iterable[A]]) -> Iterable[Iterable[A]]:
    return concat(map(lambda l: map(partial(cons, l), yss), xs))


partial = functools.partial

