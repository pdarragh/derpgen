from inspect import signature
from typing import Any, Callable, Dict, Tuple, Type, TypeVar, Union


__all__ = ['match']


Arg = TypeVar('Arg')
Val = TypeVar('Val')


def get_param_names(func: Callable) -> Tuple[str]:
    if not callable(func):
        return tuple()
    sig = signature(func)
    return tuple(sig.parameters.keys())


def match(table: Dict[Type, Union[Val, Callable[..., Val]]]) -> Callable[[Arg], Val]:
    names = {t: get_param_names(table[t]) for t in table}

    def do_match(x: Arg):
        cls = x.__class__
        v = table[cls]
        if callable(v):
            attrs = (getattr(x, name) for name in names[cls])
            return v(*attrs)
        else:
            return v

    return do_match
