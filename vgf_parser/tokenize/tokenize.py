from .vgf_token import *

import re

from typing import Dict, List, Match, NamedTuple, Optional, Pattern, Tuple, Union

RE_WHITESPACE = re.compile(r'\s+')

RE_COMMENT = re.compile(r'#(.*)$')
RE_STRING = re.compile(r'\"((?:\\.|[^\"\\])*)\"'
                       r'|'
                       r'\'((?:\\.|[^\'\\])*)\'')
RE_BRACED_TEXT = re.compile(r'{([^}]+)}')
RE_BRACKETED_TEXT = re.compile(r'<([^>]+)>')
RE_CAPITAL_TEXT = re.compile(r'([A-Z][a-z_]+)')  # This pattern *must* be used before RE_ALL_CAPITAL_TEXT.
RE_ALL_CAPITAL_TEXT = re.compile(r'([A-Z_]+)')
RE_LOWERCASE_TEXT = re.compile(r'([a-z_]+)')

CONSTANT_TOKEN_RES: List[Tuple[Pattern, Type[ConstantToken]]] = [(re.compile(re.escape(cls.match_text)), cls)
                                                                 for cls in CONSTANT_TOKENS]
NON_CONSTANT_RES: List[Tuple[Pattern, Type[VgfToken]]] = [
    (RE_COMMENT, CommentToken),
    (RE_STRING, StringToken),
    (RE_BRACED_TEXT, BracedTextToken),
    (RE_BRACKETED_TEXT, BracketedTextToken),
    (RE_CAPITAL_TEXT, CapitalWordToken),
    (RE_ALL_CAPITAL_TEXT, AllCapitalWordToken),
    (RE_LOWERCASE_TEXT, LowercaseWordToken),
]


class TokenizerError(RuntimeError):
    pass  # TODO: Improve error production.


# Regular expression magic class for making if/else matching simpler. Idea from:
#   http://code.activestate.com/recipes/456151-using-rematch-research-and-regroup-in-if-elif-elif/
class LongestRegexMatcher:
    def __init__(self, line: str):
        self._line = line
        self._match = None

    def match(self, pattern: Pattern) -> Match:
        self._match = pattern.match(self._line)
        return self._match

    @property
    def end(self) -> int:
        return self._match.end()

    def group(self, grp: Union[int, str]) -> str:
        return self._match.group(grp)

    def __next__(self):
        self._line = self._line[self.end:]

    def __bool__(self) -> bool:
        return bool(self._line)


def tokenize_grammar_file(filename: str) -> List[VgfToken]:
    line_no = 0
    tokens = []
    with open(filename) as f:
        for line in f:
            line_no += 1
            tokenize_line(line, tokens)
    return tokens


def tokenize_line(line: str, tokens: List[VgfToken]):
    if not line:
        return
    matcher = LongestRegexMatcher(line)
    while matcher:
        process_next_match(matcher, tokens)
        next(matcher)


def process_next_match(matcher: LongestRegexMatcher, tokens: List[VgfToken]):
    if matcher.match(RE_WHITESPACE):
        pass
    else:
        for pattern, cls in CONSTANT_TOKEN_RES:
            if matcher.match(pattern):
                tokens.append(cls())
                return
        for pattern, cls in NON_CONSTANT_RES:
            if matcher.match(pattern):
                tokens.append(cls(matcher.group(1)))
                return
