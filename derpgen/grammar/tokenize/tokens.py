from derpgen.utility import has_class

from dataclasses import dataclass
from enum import Enum, unique
from re import compile as re_compile, escape as re_escape
from typing import Pattern, Tuple


__all__ = ['BRACE_PAIRS', 'TokenTypes', 'TokenTypeClasses', 'Token']


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
    ENDMARKER       = (ENDMARKER_TAG,   '',                         False)
    # Whitespace
    WHITESPACE      = (auto(),          r'\s+',                     True)
    NEWLINE         = (auto(),          r'\n',                      True)
    # Comments
    COMMENT         = (auto(),          r'#.*',                     True)
    # Cases
    SNAKE_CASE      = (auto(),          r'[a-z](?:_|[a-z])*',       True)
    CAP_SNAKE_CASE  = (auto(),          r'[A-Z](?:_|[A-Z])*',       True)
    PASCAL_CASE     = (auto(),          r'[A-Z][a-zA-Z]*',          True)
    CAMEL_CASE      = (auto(),          r'[a-z][a-zA-Z]*',          True)
    # Quotes
    DBL_QUOTE_STR   = (auto(),          r'\"((?:\\.|[^\"\\])*)\"',  True)
    SNGL_QUOTE_STR  = (auto(),          r'\'((?:\\.|[^\'\\])*)\'',  True)
    # Section marker
    SECTION         = (auto(),          r'%[^%]+%',                 True)
    # Rule dividers
    SUBST           = (auto(),          '::=',                      False)
    STICK           = (auto(),          '|',                        False)
    # Operators
    EQUAL           = (auto(),          '=',                        False)
    RE_EQUAL        = (auto(),          '^=',                       False)
    COLON           = (auto(),          ':',                        False)
    # Group
    L_PAR           = (auto(),          '(',                        False)
    R_PAR           = (auto(),          ')',                        False)
    # Optional (0 or 1)
    L_BRK           = (auto(),          '[',                        False)
    R_BRK           = (auto(),          ']',                        False)
    # Repetition (0 or more)
    L_BRC           = (auto(),          '{',                        False)
    R_BRC           = (auto(),          '}',                        False)
    # Nonempty repetition (1 or more)
    L_ABR           = (auto(),          '<',                        False)
    R_ABR           = (auto(),          '>',                        False)

    def __init__(self, tag: int,  string: str, is_escaped: bool):
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


BRACE_PAIRS = {
    TokenTypes.L_PAR: TokenTypes.R_PAR,
    TokenTypes.R_PAR: TokenTypes.L_PAR,
    TokenTypes.L_BRK: TokenTypes.R_BRK,
    TokenTypes.R_BRK: TokenTypes.L_BRK,
    TokenTypes.L_BRC: TokenTypes.R_BRC,
    TokenTypes.R_BRC: TokenTypes.L_BRC,
    TokenTypes.L_ABR: TokenTypes.R_ABR,
    TokenTypes.R_ABR: TokenTypes.L_ABR,
}


# PyCharm thinks _auto_int hasn't been used yet at this point, but it was used during creation of the TokenTypes class.
# noinspection PyRedeclaration
_auto_int = 0


@unique
class TokenTypeClasses(Enum):
    EOF             = (auto(), (TokenTypes.ENDMARKER, ))
    WHITESPACE      = (auto(), (TokenTypes.WHITESPACE, TokenTypes.NEWLINE))
    COMMENTS        = (auto(), (TokenTypes.COMMENT, ))
    LOW_CASES       = (auto(), (TokenTypes.SNAKE_CASE, TokenTypes.CAMEL_CASE))
    CAP_CASES       = (auto(), (TokenTypes.CAP_SNAKE_CASE, TokenTypes.PASCAL_CASE))
    CASES           = (auto(), (TokenTypes.SNAKE_CASE, TokenTypes.CAP_SNAKE_CASE, TokenTypes.PASCAL_CASE,
                                TokenTypes.CAMEL_CASE))
    QUOTES          = (auto(), (TokenTypes.DBL_QUOTE_STR, TokenTypes.SNGL_QUOTE_STR))
    SECTIONS        = (auto(), (TokenTypes.SECTION, ))
    DIVIDERS        = (auto(), (TokenTypes.SUBST, TokenTypes.STICK))
    OPERATORS       = (auto(), (TokenTypes.EQUAL, TokenTypes.RE_EQUAL, TokenTypes.COLON))
    PARENS          = (auto(), (TokenTypes.L_PAR, TokenTypes.R_PAR))
    BRACKETS        = (auto(), (TokenTypes.L_BRK, TokenTypes.R_BRK))
    BRACES          = (auto(), (TokenTypes.L_BRC, TokenTypes.R_BRC))
    ANGLE_BRACKETS  = (auto(), (TokenTypes.L_ABR, TokenTypes.R_ABR))
    GROUPS          = (auto(), (TokenTypes.L_PAR, TokenTypes.R_PAR,
                                TokenTypes.L_BRK, TokenTypes.R_BRK,
                                TokenTypes.L_BRC, TokenTypes.R_BRC,
                                TokenTypes.L_ABR, TokenTypes.R_ABR))

    def __init__(self, tag: int, types: Tuple[TokenTypes]):
        self.tag = tag
        self.types = types

    def __eq__(self, other) -> bool:
        if other not in TokenTypeClasses:
            return NotImplemented
        return self.tag == other.tag

    def __contains__(self, token_type) -> bool:
        if not has_class(token_type, TokenTypes):
            return NotImplemented
        return token_type in self.types

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
        return f"<{self.type.name} | {self.line_no}:{self.position} | '{self.value}'>"
