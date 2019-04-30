from typing import Any, Type


def has_class(o: Any, c: Type) -> bool:
    return o.__class__ is c
