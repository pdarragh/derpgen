from .vgf_token import *

import re

from typing import List, Match, Optional, Pattern, Tuple, Type, Union


__all__ = ['tokenize_grammar_file']


RE_WHITESPACE = re.compile(r'(\s+)')

RE_ASSIGN = re.compile(r'(' + re.escape(AssignToken.match_text) + r')')
RE_PIPE = re.compile(r'(' + re.escape(PipeToken.match_text) + r')')
RE_COLON = re.compile(r'(' + re.escape(ColonToken.match_text) + r')')
RE_STAR = re.compile(r'(' + re.escape(StarToken.match_text) + r')')
RE_PLUS = re.compile(r'(' + re.escape(PlusToken.match_text) + r')')
RE_AMPERSAND_STAR = re.compile(r'(' + re.escape(AmpersandStarToken.match_text) + r')')
RE_AMPERSAND_PLUS = re.compile(r'(' + re.escape(AmpersandPlusToken.match_text) + r')')
RE_QUESTION_MARK = re.compile(r'(' + re.escape(QuestionMarkToken.match_text) + r')')

RE_COMMENT = re.compile(r'#(.*)$')
RE_STRING = re.compile(r'\"((?:\\.|[^\"\\])*)\"'
                       r'|'
                       r'\'((?:\\.|[^\'\\])*)\'')
RE_BRACED_TEXT = re.compile(r'{([^}]+)}')
RE_BRACKETED_TEXT = re.compile(r'<([^>]+)>')
RE_CAPITAL_TEXT = re.compile(r'([A-Z]\w+)')
RE_ALL_CAPITAL_TEXT = re.compile(r'([A-Z_]+)')
RE_LOWERCASE_TEXT = re.compile(r'([a-z]\w+)')

ALL_RES: List[Tuple[Pattern, Type[VgfToken]]] = [
    (RE_WHITESPACE, WhitespaceToken),

    (RE_ASSIGN, AssignToken),
    (RE_PIPE, PipeToken),
    (RE_COLON, ColonToken),
    (RE_STAR, StarToken),
    (RE_PLUS, PlusToken),
    (RE_AMPERSAND_STAR, AmpersandStarToken),
    (RE_AMPERSAND_PLUS, AmpersandPlusToken),
    (RE_QUESTION_MARK, QuestionMarkToken),

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
        self._line: str = line
        self._match: Optional[Match] = None
        self._cls: Optional[Type[VgfToken]] = None

    def match(self, pattern: Pattern, cls: Type[VgfToken]):
        match = pattern.match(self._line)
        if self._match is None:
            if match is not None:
                self._match = match
                self._cls = cls
            return
        if match is not None:
            if match.end() > self.end:
                self._match = match
                self._cls = cls

    @property
    def end(self) -> int:
        return self._match.end()

    @property
    def length(self) -> int:
        return self.end

    @property
    def line_repr(self) -> str:
        return repr(self._line)

    def group(self, grp: Union[int, str]) -> str:
        return self._match.group(grp)

    def emit(self, line_no: int, char_no: int) -> VgfToken:
        if self._match is None:
            raise TokenizerError(f"No match produced for line: {self.line_repr}")
        return self._cls(self.group(1), line_no, char_no)

    def advance(self):
        self._line = self._line[self.end:]
        self._match = None
        self._cls = None

    def __bool__(self) -> bool:
        return bool(self._line)


def tokenize_grammar_file(filename: str) -> List[VgfToken]:
    line_no = 0
    tokens = []
    with open(filename) as f:
        for line in f:
            line_no += 1
            tokenize_line(line, line_no, tokens)
    return tokens


def tokenize_line(line: str, line_no: int, tokens: List[VgfToken]):
    if not line:
        return
    matcher = LongestRegexMatcher(line)
    char_no = 1
    while matcher:
        for pattern, cls in ALL_RES:
            matcher.match(pattern, cls)
        tokens.append(matcher.emit(line_no, char_no))
        char_no += matcher.length
        matcher.advance()
