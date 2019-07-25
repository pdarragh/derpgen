from .tokens import *

from typing import Iterable, Iterator, Match, Optional


__all__ = ['LineTokenizer', 'TokenizerError']


class TokenizerError(Exception):
    pass


class LineTokenizer(Iterable[Token]):
    def __init__(self, line: str, line_no: int):
        self._line = line
        self._line_no = line_no
        self._position = 1
        self._match: Optional[Match] = None
        self._token_type: Optional[TokenTypes] = None
        self._finished = False

    def __bool__(self) -> bool:
        return bool(self._line)

    def __iter__(self) -> Iterator[Token]:
        return self

    def __next__(self) -> Token:
        if self._finished:
            raise StopIteration
        elif not self:
            self._finished = True
            return Token('\n', self._line_no, self._position + 1, TokenTypes.NEWLINE)
        else:
            self._match = None
            for token_type in TokenTypes:
                self._match_if_longest(token_type)
            if self._match is None:
                raise TokenizerError()
            text = self._match.group(0)
            self._line = self._line[len(text):]
            self._position += len(text)
            return Token(text, self._line_no, self._position, self._token_type)

    @property
    def position(self) -> int:
        return self._position

    @property
    def remaining_text(self) -> str:
        return self._line

    def _match_if_longest(self, token_type: TokenTypes):
        match = token_type.regex.match(self._line)
        # Only update the _match if the new match is longer.
        if match is not None and (self._match is None or len(match.group(0)) > len(self._match.group(0))):
            self._match = match
            self._token_type = token_type
