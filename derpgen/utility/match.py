from inspect import signature
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union


__all__ = ['match', 'match_pred']


Val = TypeVar('Val')


def get_param_names(func: Callable) -> Tuple[str]:
    if not callable(func):
        return tuple()
    sig = signature(func)
    return tuple(sig.parameters.keys())


def match(table: Dict[Type, Union[Val, Callable[..., Val]]], params: Optional[Tuple[str, ...]] = None,
          pos: int = 0) -> Callable[..., Val]:
    if params is None:
        params = ()

    names = {t: get_param_names(table[t]) for t in table}

    def do_match(*args: Any):
        x = args[pos]
        cls = x.__class__
        v = table[cls]
        if callable(v):
            param_args = {param: args[i] for (i, param) in enumerate(params)}
            call_args = (param_args[name] if name in param_args else getattr(x, name) for name in names[cls])
            return v(*call_args)
        else:
            return v

    return do_match


def match_pred(table: Dict[Type, Dict[Callable[..., bool], Union[Val, Callable[..., Val]]]],
               params: Optional[Tuple[str, ...]] = None, pos: int = 0) -> Callable[..., Val]:
    if params is None:
        params = ()

    names = {t: {p: get_param_names(v) for p, v in table[t].items()} for t in table}
    pred_names = {t: {p: get_param_names(p) for p in table[t]} for t in table}

    def do_pred_match(*args: Any):
        x = args[pos]
        cls = x.__class__
        preds = table[cls]
        for pred, v in preds.items():
            param_args = {param: args[i] for (i, param) in enumerate(params)}
            pred_args = (param_args[name] if name in param_args else getattr(x, name) for name in pred_names[cls][pred])
            if not pred(*pred_args):
                continue
            if callable(v):
                call_args = (param_args[name] if name in param_args else getattr(x, name) for name in names[cls][pred])
                return v(*call_args)
            else:
                return v

    return do_pred_match
