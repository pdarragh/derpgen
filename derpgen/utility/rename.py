from inspect import currentframe


__all__ = ['RENAME_MARKER', 'rename_marked_funcs']


RENAME_MARKER = '__rename_me'


def rename_marked_funcs():
    funcs_to_update = {}

    for name, val in currentframe().f_back.f_locals.items():
        if callable(val) and hasattr(val, RENAME_MARKER) and getattr(val, RENAME_MARKER) is True:
            funcs_to_update[name] = val

    for name, func in funcs_to_update.items():
        func.__name__ = name
        func.__qualname__ = name
