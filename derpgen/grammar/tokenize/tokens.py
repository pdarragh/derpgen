from dataclasses import dataclass
from enum import Enum, unique
from re import compile as re_compile, escape as re_escape
from typing import Pattern


__all__ = ['TokenTypes', 'Token']


ENDMARKER_TAG = 0
_auto_int = ENDMARKER_TAG + 1


def auto() -> int:
    global _auto_int
    val = _auto_int
    _auto_int += 1
    return val


@unique
class TokenTypes(Enum):
    # Endmarker
    # See __init__ below for more information about how the endmarker works.
    ENDMARKER       = ('',                      False,  ENDMARKER_TAG)
    # Whitespace
    WHITESPACE      = (r'\s+',                  True,   auto())
    NEWLINE         = (r'\n',                   True,   auto())
    # Comments
    COMMENT         = (r'#.*',                  True,   auto())
    # Cases
    SNAKE_CASE      = (r'[a-z](?:_|[a-z])*',    True,   auto())
    CAP_SNAKE_CASE  = (r'[A-Z](?:_|[A-Z])*',    True,   auto())
    PASCAL_CASE     = (r'[A-Z][a-zA-Z]*',       True,   auto())
    CAMEL_CASE      = (r'[a-z][a-zA-Z]*',       True,   auto())
    # Quotes
    DBL_QUOTE_STR   = (r'\"(?:\\.|[^\"\\])*\"', True,   auto())
    SNGL_QUOTE_STR  = (r'\'(?:\\.|[^\'\\])*\'', True,   auto())
    # Operators
    SUBST           = ('::=',                   False,  auto())
    EQUAL           = ('=',                     False,  auto())
    RE_EQUAL        = ('^=',                    False,  auto())
    COLON           = (':',                     False,  auto())
    PIPE            = ('|',                     False,  auto())
    MODULO          = ('%',                     False,  auto())
    # Group
    L_PAR           = ('(',                     False,  auto())
    R_PAR           = (')',                     False,  auto())
    # Optional (0 or 1)
    L_BRK           = ('[',                     False,  auto())
    R_BRK           = (']',                     False,  auto())
    # Repetition (0 or more)
    L_BRC           = ('{',                     False,  auto())
    R_BRC           = ('}',                     False,  auto())
    # Nonempty repetition (1 or more)
    L_ABR           = ('<',                     False,  auto())
    R_ABR           = ('>',                     False,  auto())

    def __init__(self, string: str, is_escaped: bool, tag: int):
        self.tag: int = tag
        # The endmarker token should never match anything, because there is no regular expression that can correctly
        # match its intended use. Therefore the endmarker will need to be manually added at the end of tokenization.
        if self.tag == ENDMARKER_TAG:
            # We create a fake regex Pattern object which will not successfully match against anything. This is done by
            # using dummy functions which don't do anything.
            class EndmarkerPattern:
                pass
            pattern = EndmarkerPattern()
            pattern.search      = lambda _,          *args, **kwargs: None
            pattern.match       = lambda _,          *args, **kwargs: None
            pattern.fullmatch   = lambda _,          *args, **kwargs: None
            pattern.split       = lambda _, s,       *args, **kwargs: s
            pattern.findall     = lambda _,          *args, **kwargs: []
            pattern.finditer    = lambda _,          *args, **kwargs: iter([])
            pattern.sub         = lambda _, repl, s, *args, **kwargs: s
            pattern.subn        = lambda _, repl, s, *args, **kwargs: (s, 0)
            self.regex: Pattern = pattern
        else:
            escaped = string if is_escaped else re_escape(string)
            self.regex: Pattern = re_compile(escaped)

    def __eq__(self, other) -> bool:
        if other not in TokenTypes:
            return NotImplemented
        return self.tag == other.tag

    def __hash__(self) -> int:
        return self.tag


@dataclass
class Token:
    value: str
    line_no: int
    position: int
    type: TokenTypes

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"<{self.type.name} | {self.line_no}:{self.position} | {self.value}>"
