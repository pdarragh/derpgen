from .production import *
from .production_part import *
from ..tokenize import *

from derpgen.utility import has_class

from itertools import chain
from typing import Dict, List, NamedTuple, Set, Tuple, Type


__all__ = ['RuleDict', 'RegexDict', 'SectionsParse', 'parse_grammar_file']

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


RuleDict = Dict[str, List[Production]]
RegexDict = Dict[str, str]
ParameterParse = NamedTuple('ParameterParse', [('part', ProductionPart), ('idx', int)])
SectionsParse = NamedTuple('SectionsParse', [('grammar_parse', RuleDict), ('tokens_parse', RegexDict)])

GRAMMAR_SECTION = 'grammar'
TOKENS_SECTION = 'tokens'


class ParserError(RuntimeError):
    pass  # TODO: Improve error production.


def parse_grammar_file(filename: str) -> SectionsParse:
    # Lex the grammar, then strip all whitespace and comments.
    tokens = list(filter(lambda t: not (has_class(t, WhitespaceToken) or has_class(t, CommentToken)),
                         tokenize_grammar_file(filename)))
    if not tokens:
        raise ParserError(f"Empty file: {filename}.")
    sections = break_sections(tokens)
    parse = parse_sections(sections)
    return parse


def parse_sections(sections: Dict[str, List[VgfToken]]) -> SectionsParse:
    grammar_tokens = sections.get(GRAMMAR_SECTION)
    if grammar_tokens is None:
        raise ParserError(f"No grammar section defined.")
    grammar_parse = parse_grammar_section(grammar_tokens)
    needed_definitions = identify_needed_token_definitions(grammar_parse)
    tokens_tokens = sections.get(TOKENS_SECTION)
    tokens_parse = parse_tokens_section(tokens_tokens)
    missing_definitions = needed_definitions.difference(tokens_parse.keys())
    if missing_definitions:
        raise ParserError(f"Missing definitions for the following special tokens: {', '.join(missing_definitions)}.")
    return SectionsParse(grammar_parse, tokens_parse)


def identify_needed_token_definitions(rules: RuleDict) -> Set[str]:
    needed_definitions = set()
    for token in chain(*rules.values()):
        if has_class(token, AllCapitalWordToken):
            needed_definitions.add(token.text)
    return needed_definitions


def break_sections(tokens: List[VgfToken]) -> Dict[str, List[VgfToken]]:
    # The first token must be a SectionToken to start the first section.
    if not has_class(tokens[0], DirectiveToken):
        raise ParserError(f"Expected section token ('%section') at beginning of file; instead found {str(tokens[0])}.")

    sections: Dict[str, List[VgfToken]] = {}
    section_tokens: List[Tuple[int, DirectiveToken]] = list(filter(lambda p: has_class(p[1], DirectiveToken),
                                                                   enumerate(tokens)))
    # Add a dummy section token to help with slicing the last section.
    section_tokens.append((len(tokens), DirectiveToken("DUMMY_SECTION", -1, -1)))
    # Extract initial info from first section token.
    prev_idx, tok = section_tokens[0]
    section_name = tok.text
    for idx, tok in section_tokens[1:]:
        # Get the next slice, leaving out the initial SectionToken.
        token_slice = tokens[prev_idx+1:idx]
        # Add the slice to the section.
        section = sections.get(section_name, [])
        section.extend(token_slice)
        sections[section_name] = section
        # Update info for next section slice.
        prev_idx = idx
        section_name = tok.text
    return sections


def parse_tokens_section(tokens: List[VgfToken]) -> RegexDict:
    idx = 0

    def next_token() -> VgfToken:
        nonlocal idx
        idx += 1
        return tokens[idx]

    regexes: RegexDict = {}
    while idx < len(tokens):
        token = tokens[idx]
        if has_class(token, AllCapitalWordToken):
            name = token.text
            if name in regexes:
                raise ParserError(f"Duplicate definition for special token {name} on line {token.line_no} "
                                  f"at position {token.char_no}.")
            token = next_token()
            if not has_class(token, EqualsToken):
                raise ParserError(f"Expected equals token ('=') after special token name on line {token.line_no} "
                                  f"at position {token.char_no}; instead found {str(token)}.")
            token = next_token()
            if not has_class(token, StringToken):
                raise ParserError(f"Expected string token (''...'' or '\"...\"') after equals token "
                                  f"on line {token.line_no} at position {token.char_no}; instead found {str(token)}.")
            regexes[name] = token.text
            idx += 1
        else:
            raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} at position {token.char_no}; "
                              f"expected new special token definition.")
    return regexes


def parse_grammar_section(tokens: List[VgfToken]) -> RuleDict:
    idx = 0

    def next_token() -> VgfToken:
        nonlocal idx
        idx += 1
        return tokens[idx]

    rules: RuleDict = {}
    while idx < len(tokens):
        token = tokens[idx]
        if has_class(token, BracketedTextToken):
            rule_name = token.text
            if rule_name in rules:
                raise ParserError(f"Duplicate definition for rule {rule_name} on line {token.line_no} "
                                  f"at position {token.char_no}.")
            token = next_token()
            if not has_class(token, AssignToken):
                raise ParserError(f"Expected assign token ('::=') after rule name on line {token.line_no} "
                                  f"at position {token.char_no}; instead found {str(token)}.")
            token = next_token()
            if has_class(token, PipeToken):
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
        if has_class(tokens[idx], BracketedTextToken):
            if idx + 1 < len(tokens):
                if has_class(tokens[idx + 1], AssignToken):
                    return False
        return True

    def in_production() -> bool:
        if not in_rule():
            return False
        return not has_class(tokens[idx], PipeToken)

    start = idx
    while idx < len(tokens) and in_rule():
        token: VgfToken = tokens[idx]
        if idx != start:
            # Except for the first production of a rule, all productions must begin with a pipe token ('|').
            if not has_class(token, PipeToken):
                raise ParserError(f"Expected pipe token ('|') to begin new production on line {token.line_no} "
                                  f"at position {token.char_no}; instead found {str(token)}.")
            idx += 1
            check_in_bounds(tokens, idx, 'new production')
            token = tokens[idx]
        # Now process the production, beginning after the pipe.
        if has_class(token, BracketedTextToken):
            token: BracketedTextToken
            # The current token is a rule alias.
            if token.text == rule_name:
                # But the rule is recursive.
                raise ParserError(f"Recursive rule alias for rule {rule_name} on line {token.line_no} "
                                  f"at position {token.char_no}.")
            production = RuleAliasProduction(RuleNamePart(token))
            productions.append(production)
            idx += 1
        elif has_class(token, CapitalWordToken):
            token: CapitalWordToken
            # The current token begins a non-aliasing production definition.
            name = ProductionNamePart(token)
            parts: List[ProductionPart] = []
            idx += 1
            while in_production():
                token: VgfToken = tokens[idx]
                if has_class(token, StringToken):
                    token: StringToken
                    part = LiteralPart(token)
                    parts.append(part)
                    idx += 1
                elif has_class(token, AllCapitalWordToken):
                    token: AllCapitalWordToken
                    part = SpecialPart(token)
                    parts.append(part)
                    idx += 1
                elif has_class(token, LowercaseWordToken):
                    token: LowercaseWordToken
                    name = token
                    idx += 1
                    check_in_bounds(tokens, idx, f'parameter {str(token)}')
                    if not has_class(tokens[idx], ColonToken):
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
    token: VgfToken = tokens[idx]
    if has_class(token, StringToken):
        token: StringToken
        actual = LiteralPart(token)
    elif has_class(token, AllCapitalWordToken):
        token: AllCapitalWordToken
        actual = SpecialPart(token)
    elif has_class(token, BracketedTextToken):
        token: BracketedTextToken
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
    if has_class(token, StarToken):
        modified = ListPart(actual)
    elif has_class(token, PlusToken):
        modified = NonemptyListPart(actual)
    elif has_class(token, AmpersandStarToken):
        idx += 1
        check_in_bounds(tokens, idx, 'separated list')
        token = tokens[idx]
        modified = parse_braced_text(token, actual, SeparatedListPart)
    elif has_class(token, AmpersandPlusToken):
        idx += 1
        check_in_bounds(tokens, idx, 'nonempty separated list')
        token = tokens[idx]
        modified = parse_braced_text(token, actual, NonemptySeparatedListPart)
    elif has_class(token, QuestionMarkToken):
        modified = OptionalPart(actual)
    else:
        raise ParserError(f"Unknown ModifierPart subclass {type(token).__name__} encountered on line {token.line_no} "
                          f"at position {token.char_no}; please contact the developers.")
    return ParameterParse(modified, idx + 1)


def parse_braced_text(token: VgfToken, actual: ActualPart, cls: Type[SeparatedPart]) -> ModifiedPart:
    if not has_class(token, BracedTextToken):
        raise ParserError(f"Unexpected token {str(token)} on line {token.line_no} at position {token.char_no}; "
                          f"expected braced text to denote a separator.")
    # The following arguments are not properly detected by PyCharm, so we suppress inspection.
    # noinspection PyArgumentList
    return cls(actual, ActualPart(token))
