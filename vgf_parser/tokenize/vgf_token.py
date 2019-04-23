from dataclasses import dataclass


@dataclass
class VgfToken:
    text: str
    line_no: int
    char_no: int

    def __str__(self) -> str:
        return self.text

    def __len__(self) -> int:
        return len(self.text)


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

    def __init__(self, *args, **kwargs):
        if self.match_text is None:
            raise RuntimeError("Initialization of ConstantToken without match_text specified.")
        super().__init__(*args, **kwargs)

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
