from .eq_type import *

from dataclasses import dataclass
from typing import Any, Callable, Dict, Set, Tuple, TypeVar


__all__ = ['fix', 'EqType']


Args = Tuple[Any, ...]
Key = Tuple[int, ...]
Val = TypeVar('Val')


@dataclass
class Parameters:
    visited: Set[Key]
    changed: bool
    running: bool


def fix(bottom: Val, *eqs: EqType):
    cache: Dict[Key, Val] = {}
    params = Parameters(set(), False, False)

    def is_cached(k: Key) -> bool:
        return k in cache

    def is_visited(k: Key) -> bool:
        return k in params.visited

    def cached_val(k: Key) -> Val:
        val = cache.get(k)
        if val is None:
            return bottom
        else:
            return val

    def f(func: Callable[..., Val], key: Key, *args: Any) -> Val:
        if is_visited(key):
            if is_cached(key):
                return cached_val(key)
            else:
                return bottom
        else:
            params.visited.add(key)
            val = func(*args)
            if val != cached_val(key):
                params.changed = True
                cache[key] = val
            return val

    def decorate(func: Callable[[Key], Val]):
        def wrapper(*args: Any):
            key = tuple(get_eq_hash(eqs[i], arg) for (i, arg) in enumerate(args))
            if params.running:
                f(func, *args)
            elif is_cached(key):
                cached_val(key)
            else:
                val = bottom
                params.visited = set()
                params.changed = True
                params.running = True
                while params.changed:
                    params.changed = False
                    params.visited = set()
                    val = f(func, key, *args)
                params.running = False
                return val
        return wrapper

    return decorate
