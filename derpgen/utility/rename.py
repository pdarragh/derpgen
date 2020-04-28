from inspect import currentframe


__all__ = ['RENAME_MARKER', 'rename_marked_funcs']


RENAME_MARKER = '__rename_me'

# TODO:
"""
Instead of requiring a user call to rename_marked_funcs(), instead have functions that require the use of this to add
their wrapped functions to a global list, and then prior to the execution of any of them run this function automatically
"""

def rename_marked_funcs():
    funcs_to_update = {}

    for name, val in currentframe().f_back.f_locals.items():
        if callable(val) and hasattr(val, RENAME_MARKER) and getattr(val, RENAME_MARKER) is True:
            funcs_to_update[name] = val

    for name, func in funcs_to_update.items():
        func.__name__ = name
        func.__qualname__ = name
