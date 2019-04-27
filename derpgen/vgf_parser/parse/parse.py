from .production import *
from .production_part import *

from typing import Dict, List, NamedTuple, Type


__all__ = ['parse_grammar_file']

"""
The following is a (simplified) representation of the grammar for VGF files as
recognized by this parser.

<rule>              ::= <rule_name> '::=' '|'? <production>&+{'|'}
<production>        ::= CAP_WORD <part>+
                      | <rule_name>
<part>              ::= <actual> <modifier>?
                      | <parameter>
<parameter>         ::= LOW_WORD ':' <actual> <modifier>?
<actual>            ::= '"' STRING '"'
                      | '\'' STRING '\''
                      | ALL_CAP_WORD
                      | <rule_name>
<modifier>          ::= '?'
                      | '*'
                      | '+'
                      | '&*' '{' STRING '}'
                      | '&+' '{' STRING '}'
<rule_name>         ::= '<' LOW_WORD '>'

The special tokens correspond to the following meanings:
    LOW_WORD
        A word consisting only of lowercase letters and underscores.
        Note that the first character must be a lowercase letter.
    CAP_WORD
        A word which begins with an uppercase letter and contains at least one
        lowercase letter somewhere. Underscores are also acceptable.
    ALL_CAP_WORD
        A word consisting only of uppercase letters and underscores.
        Note that the first character must be an uppercase letter.
    STRING
        Any literal string of text.
"""


ParameterParse = NamedTuple('TokenParse', [('part', ProductionPart), ('idx', int)])


class ParserError(RuntimeError):
    pass  # TODO: Improve error production.


def parse_grammar_file(filename: str) -> Dict[str, List[Production]]:
    # Lex the grammar, then strip all whitespace and comments.
    tokens = list(filter(lambda t: not (isinstance(t, WhitespaceToken) or isinstance(t, CommentToken)),
                         tokenize_grammar_file(filename)))
    parsed_rules = parse_rules(tokens)
    return parsed_rules


def parse_rules(tokens: List[VgfToken]) -> Dict[str, List[Production]]:
    idx = 0

    def next_token() -> VgfToken:
        nonlocal idx
        idx += 1
        return tokens[idx]

    rules: Dict[str, List[Production]] = {}
    while idx < len(tokens):
        token = tokens[idx]
        if isinstance(token, WhitespaceToken):
            idx += 1
        elif isinstance(token, CommentToken):
            idx += 1
        elif isinstance(token, BracketedTextToken):
            rule_name = token.text
            if rule_name in rules:
                raise ParserError(f"Duplicated definition for rule {rule_name} on line {token.line_no} "
                                  f"at position {token.char_no}.")
            token = next_token()
            if not isinstance(token, AssignToken):
                raise ParserError(f"Expected assign token ('::=') after rule name on line {token.line_no} "
                                  f"at position {token.char_no}; instead found {str(token)}.")
            token = next_token()
            if isinstance(token, PipeToken):
                # An initial pipe is optional.
                token = next_token()
            productions = []
            rules[rule_name] = productions
            span = parse_rule(rule_name, tokens, idx, productions)
            if span == 0:
                raise ParserError(f"Empty rule definition on line {token.line_no} at position {token.char_no}.")
            idx += span
        else:
            raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} at position {token.char_no}; "
                              f"expected a new rule definition.")
    return rules


def check_in_bounds(tokens: List[VgfToken], idx: int, hint: str):
    token = tokens[idx - 1]
    if idx >= len(tokens):
        raise ParserError(f"Unexpectedly found end of file while parsing {hint} on line {token.line_no} "
                          f"at position {token.char_no}.")


def parse_rule(rule_name: str, tokens: List[VgfToken], idx: int, productions: List[Production]) -> int:

    def in_rule() -> bool:
        # Check whether we've reached the end of the file.
        if idx >= len(tokens):
            return False
        # Perform lookahead to determine whether we're at the boundary of a new rule definition.
        if isinstance(tokens[idx], BracketedTextToken):
            if idx + 1 < len(tokens):
                if isinstance(tokens[idx + 1], AssignToken):
                    return False
        return True

    def in_production() -> bool:
        if not in_rule():
            return False
        return not isinstance(tokens[idx], PipeToken)

    start = idx
    while idx < len(tokens) and in_rule():
        token = tokens[idx]
        if idx != start:
            # Except for the first production of a rule, all productions must begin with a pipe token ('|').
            if not isinstance(token, PipeToken):
                raise ParserError(f"Expected pipe token ('|') to begin new production on line {token.line_no} "
                                  f"at position {token.char_no}; instead found {str(token)}.")
            idx += 1
            check_in_bounds(tokens, idx, 'new production')
            token = tokens[idx]
        # Now process the production, beginning after the pipe.
        if isinstance(token, BracketedTextToken):
            # The current token is a rule alias.
            if token.text == rule_name:
                # But the rule is recursive.
                raise ParserError(f"Recursive rule alias for rule {rule_name} on line {token.line_no} "
                                  f"at position {token.char_no}.")
            production = RuleAliasProduction(RuleNamePart(token))
            productions.append(production)
            idx += 1
        elif isinstance(token, CapitalWordToken):
            # The current token begins a non-aliasing production definition.
            name = ProductionNamePart(token)
            parts: List[ProductionPart] = []
            idx += 1
            while in_production():
                token = tokens[idx]
                if isinstance(token, StringToken):
                    part = LiteralPart(token)
                    parts.append(part)
                    idx += 1
                elif isinstance(token, AllCapitalWordToken):
                    part = SpecialPart(token)
                    parts.append(part)
                    idx += 1
                elif isinstance(token, LowercaseWordToken):
                    name = token
                    idx += 1
                    check_in_bounds(tokens, idx, f'parameter {str(token)}')
                    if not isinstance(tokens[idx], ColonToken):
                        raise ParserError(f"Expected colon token (':') to define parameter matcher "
                                          f"on line {token.line_no} at position {token.char_no}; instead found "
                                          f"{str(tokens[idx])}.")
                    idx += 1
                    check_in_bounds(tokens, idx, f'parameter {str(token)}')
                    parse = parse_parameter(tokens, idx)
                    part = ParameterPart(name, parse.part)
                    parts.append(part)
                    idx = parse.idx
                else:
                    raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} "
                                      f"at position {token.char_no}; expected a quoted literal, an all-caps token, or "
                                      f"a parameter name.")
            production = NamedProduction(name, parts)
            productions.append(production)
        else:
            raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} at position {token.char_no}; "
                              f"expected either a rule alias or production definition.")
    return idx - start


def parse_parameter(tokens: List[VgfToken], idx: int) -> ParameterParse:
    token = tokens[idx]
    if isinstance(token, StringToken):
        actual = LiteralPart(token)
    elif isinstance(token, AllCapitalWordToken):
        actual = SpecialPart(token)
    elif isinstance(token, BracketedTextToken):
        actual = RuleNamePart(token)
    else:
        raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} at position {token.char_no}; "
                          f"expected a quoted literal, an all-caps token, or a bracketed rule name.")
    idx += 1
    if idx >= len(tokens) or not isinstance(tokens[idx], ModifierToken):
        # There's no modifier.
        return ParameterParse(actual, idx)
    # There's a modifier.
    token = tokens[idx]
    if isinstance(token, StarToken):
        modified = ListPart(actual)
    elif isinstance(token, PlusToken):
        modified = NonemptyListPart(actual)
    elif isinstance(token, AmpersandStarToken):
        idx += 1
        check_in_bounds(tokens, idx, 'separated list')
        token = tokens[idx]
        modified = parse_braced_text(token, actual, SeparatedListPart)
    elif isinstance(token, AmpersandPlusToken):
        idx += 1
        check_in_bounds(tokens, idx, 'nonempty separated list')
        token = tokens[idx]
        modified = parse_braced_text(token, actual, NonemptySeparatedListPart)
    elif isinstance(token, QuestionMarkToken):
        modified = OptionalPart(actual)
    else:
        raise ParserError(f"Unknown ModifierPart subclass {type(token).__name__} encountered on line {token.line_no} "
                          f"at position {token.char_no}; please contact the developers.")
    return ParameterParse(modified, idx + 1)


def parse_braced_text(token: VgfToken, actual: ActualPart, cls: Type[SeparatedPart]) -> ModifiedPart:
    if not isinstance(token, BracedTextToken):
        raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} at position {token.char_no}; "
                          f"expected braced text to denote a separator.")
    # The following arguments are not properly detected by PyCharm, so we suppress inspection.
    # noinspection PyArgumentList
    return cls(actual, token)
