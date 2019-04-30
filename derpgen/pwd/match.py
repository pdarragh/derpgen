from inspect import signature
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union


__all__ = ['match']


Arg = TypeVar('Arg')
Val = TypeVar('Val')


def get_param_names(func: Callable) -> Tuple[str]:
    if not callable(func):
        return tuple()
    sig = signature(func)
    return tuple(sig.parameters.keys())


def match(table: Dict[Type, Union[Val, Callable[..., Val]]], params: Optional[Tuple[str, ...]] = None,
          match_arg_pos: int = -1) -> Callable[[Arg], Val]:
    names = {t: get_param_names(table[t]) for t in table}

    def do_match(*args: Any):
        x = args[match_arg_pos]
        cls = x.__class__
        v = table[cls]
        if callable(v):
            param_args = {param: args[i] for (i, param) in enumerate(params)}
            call_args = (param_args[name] if name in param_args else getattr(x, name) for name in names[cls])
            return v(*call_args)
        else:
            return v

    return do_match
