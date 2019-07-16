from dataclasses import dataclass
from typing import Generic, TypeVar


__all__ = ['Tree', 'Empty', 'Leaf', 'Branch']


T = TypeVar('T')


@dataclass
class Tree(Generic[T]):
    pass


@dataclass
class Empty(Tree):
    pass


@dataclass
class Leaf(Tree):
    value: T


@dataclass
class Branch(Tree):
    left: Tree[T]
    right: Tree[T]
