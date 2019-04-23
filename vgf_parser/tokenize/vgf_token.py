from dataclasses import dataclass


@dataclass
class VgfToken:
    text: str


class LiteralToken(VgfToken):
    def __repr__(self) -> str:
        return f"'{self.text}'"


class SpecialToken(VgfToken):
    pass


class BracedTextToken(VgfToken):
    def __repr__(self) -> str:
        return '{' + self.text + '}'


class BracketedTextToken(VgfToken):
    def __repr__(self) -> str:
        return '<' + self.text + '>'


class CapitalWordToken(VgfToken):
    pass


class ParameterToken(VgfToken):
    pass


class ConstantToken(VgfToken):
    match_text = None

    def __init__(self):
        if self.match_text is None:
            raise RuntimeError("Initialization of ConstantToken without match_text specified.")
        super().__init__(self.match_text)


class ColonToken(ConstantToken):
    match_text = ':'


class ListToken(ConstantToken):
    match_text = '*'


class NonemptyListToken(ConstantToken):
    match_text = '+'


class SeparatedListToken(ConstantToken):
    match_text = '&*'


class NonemptySeparatedListToken(ConstantToken):
    match_text = '&+'


class OptionalToken(ConstantToken):
    match_text = '?'


CONSTANT_TOKENS = [
    ColonToken,
    ListToken,
    NonemptyListToken,
    SeparatedListToken,
    NonemptySeparatedListToken,
    OptionalToken,
]

