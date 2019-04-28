from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar


__all__ = ['EqType', 'memoize']


class EqType(Enum):
    Eq = 1      # Physical equality (pointer equality).
    Equal = 2   # Value equality.


def get_hash(o: Any, eq: EqType) -> int:
    if eq is EqType.Eq:
        return id(o)
    elif eq is EqType.Equal:
        return hash(o)
    else:
        raise RuntimeError(f"Invalid EqType: {eq}.")


Key = Tuple[Any, ...]
Val = TypeVar('Val')


def memoize(*eqs: EqType):
    cache: Dict[Key, Val] = {}

    @wraps
    def decorate(func: Callable[[Any, ...], Val]):
        def wrapper(*args: Any):  # This decorator does not support keyword arguments.
            key = tuple(get_hash(arg, eqs[i]) for (i, arg) in enumerate(args))
            val = cache.get(key)
            if val is None:
                val = func(*args)
                cache[key] = val
            return val
        return wrapper

    return decorate
