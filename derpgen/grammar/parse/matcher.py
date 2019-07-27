from dataclasses import dataclass
from typing import Pattern


__all__ = ['Matcher', 'LiteralMatcher', 'RegexMatcher']


@dataclass
class Matcher:
    name: str


@dataclass
class LiteralMatcher(Matcher):
    literal: str


@dataclass
class RegexMatcher(Matcher):
    pattern: Pattern
