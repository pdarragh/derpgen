from .tokens import *
from .tokenizer import *

from typing import List


class InvalidTokenError(Exception):
    def __init__(self, line_no: int, line: str, pos: int):
        msg = f"Invalid token on line {line_no}, character {pos}:\n"
        msg += f"{line}\n"
        msg += (" " * pos) + "^ invalid token"
        super().__init__(msg)


def tokenize_file(filename: str) -> List[Token]:
    with open(filename) as f:
        text = f.read()
    return tokenize_text(text)


def tokenize_text(text: str) -> List[Token]:
    tokens = []
    lines = text.splitlines()
    for line_no, line in enumerate(lines):
        line_tokens = []
        tokenizer = LineTokenizer(line, line_no)
        try:
            for token in tokenizer:
                line_tokens.append(token)
        except TokenizerError:
            raise InvalidTokenError(line_no, line, tokenizer.position)
        tokens.extend(line_tokens)
    tokens.append(Token('', len(lines), 0, TokenTypes.ENDMARKER))
    return tokens
