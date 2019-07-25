from .eq_type import *
from .lazy import *

from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar


__all__ = ['memoize', 'EqType']


Args = Tuple[Any, ...]
Key = Tuple[int, ...]
Val = TypeVar('Val')


def memoize(*eqs: EqType):
    cache: Dict[Key, Val] = {}

    @wraps
    def decorate(func: Callable[..., Val]):
        def wrapper(*args: Any):  # This decorator does not support keyword arguments.
            key: Key = tuple(hash_of_eq(eqs[i], arg) for (i, arg) in enumerate(args))
            val: Val = cache.get(key)
            if val is None:
                val = delay(lambda: func(*args))
                cache[key] = val
            return force(val)
        return wrapper

    return decorate
