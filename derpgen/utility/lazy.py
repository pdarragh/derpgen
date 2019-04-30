from typing import Callable, Generic, TypeVar, Union


__all__ = ['delay', 'force']


Val = TypeVar('Val')
ValFunc = Callable[[], Val]


class Lazy(Generic[Val]):
    def __init__(self, func: ValFunc):
        self.forced = False
        self.func = func
        self.val = None

    def force(self) -> Val:
        if not self.forced:
            self.forced = True
            self.val = self.func()
        return self.val


def delay(v: ValFunc) -> Lazy[Val]:
    return Lazy(lambda: v)


def force(v: Union[Lazy[Val], Val]) -> Val:
    if isinstance(v, Lazy):
        return v.force()
    else:
        return v
