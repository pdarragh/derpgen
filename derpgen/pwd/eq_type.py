from enum import Enum
from typing import Any


__all__ = ['EqType', 'get_eq_hash']


class EqType(Enum):
    Eq = 1      # Physical equality (pointer equality).
    Equal = 2   # Value equality.


def get_eq_hash(eq_type: EqType, o: Any) -> int:
    if eq_type is EqType.Eq:
        return id(o)
    elif eq_type is EqType.Equal:
        return hash(o)
    else:
        raise RuntimeError(f"Invalid EqType: {eq_type}.")
