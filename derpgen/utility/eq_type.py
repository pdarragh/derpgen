from enum import Enum, auto, unique
from typing import Any


__all__ = ['EqType', 'hash_of_eq']


@unique
class EqType(Enum):
    Eq = auto()     # Physical equality (pointer equality).
    Equal = auto()  # Value equality.


def hash_of_eq(eq_type: EqType, o: Any) -> int:
    if eq_type is EqType.Eq:
        return id(o)
    elif eq_type is EqType.Equal:
        return hash(o)
    else:
        raise RuntimeError(f"Invalid EqType: {eq_type}.")
