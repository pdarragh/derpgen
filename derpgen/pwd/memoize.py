from .eq_type import *
from .lazy import *

from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar


__all__ = ['EqType', 'memoize']


Args = Tuple[Any, ...]
Key = Tuple[int, ...]
Val = TypeVar('Val')


def memoize(*eqs: EqType):
    cache: Dict[Key, Val] = {}

    @wraps
    def decorate(func: Callable[[Any, ...], Val]):
        def wrapper(*args: Any):  # This decorator does not support keyword arguments.
            key: Key = tuple(get_eq_hash(eqs[i], arg) for (i, arg) in enumerate(args))
            val: Val = cache.get(key)
            if val is None:
                val = delay(lambda: func(*args))
                cache[key] = val
            return force(val)
        return wrapper

    return decorate
