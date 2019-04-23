from dataclasses import dataclass


@dataclass
class VgfToken:
    text: str

    def __str__(self) -> str:
        return self.text


class WhitespaceToken(VgfToken):
    pass


class CommentToken(VgfToken):
    def __str__(self) -> str:
        return '#' + self.text


class StringToken(VgfToken):
    def __str__(self) -> str:
        return f"'{self.text}'"


class BracedTextToken(VgfToken):
    def __str__(self) -> str:
        return '{' + self.text + '}'


class BracketedTextToken(VgfToken):
    def __str__(self) -> str:
        return '<' + self.text + '>'


class CapitalWordToken(VgfToken):
    pass


class AllCapitalWordToken(VgfToken):
    pass


class LowercaseWordToken(VgfToken):
    pass


class ConstantToken(VgfToken):
    match_text = None

    def __init__(self, text: str):
        if self.match_text is None:
            raise RuntimeError("Initialization of ConstantToken without match_text specified.")
        super().__init__(text)

    def __str__(self) -> str:
        return self.match_text


class RuleDefinitionToken(ConstantToken):
    match_text = '::='


class ProductionSeparationToken(ConstantToken):
    match_text = '|'


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
