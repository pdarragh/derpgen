from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar


__all__ = ['EqType', 'memoize']


Args = Tuple[Any, ...]
Key = Tuple[int, ...]
Val = TypeVar('Val')


class EqType(Enum):
    Eq = 1      # Physical equality (pointer equality).
    Equal = 2   # Value equality.


def get_hash(eq_type: EqType, o: Any) -> int:
    if eq_type is EqType.Eq:
        return id(o)
    elif eq_type is EqType.Equal:
        return hash(o)
    else:
        raise RuntimeError(f"Invalid EqType: {eq_type}.")


def memoize(*eqs: EqType):
    cache: Dict[Args, Val] = {}

    @wraps
    def decorate(func: Callable[[Any, ...], Val]):
        def wrapper(*args: Any):  # This decorator does not support keyword arguments.
            key: Key = tuple(get_hash(eqs[i], arg) for (i, arg) in enumerate(args))
            val: Val = cache.get(key)
            if val is None:
                val = func(*args)
                cache[key] = val
            return val
        return wrapper

    return decorate
