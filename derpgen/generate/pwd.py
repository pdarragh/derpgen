from ..grammar import AST

from derpgen.utility import *

from dataclasses import dataclass
from typing import Callable, Dict, Generic, List, TypeVar


Token = TypeVar('Token')
RedFunc = Callable[[AST], AST]


@dataclass
class Grammar(Generic[Token]):
    pass


@dataclass
class Nil(Grammar[Token]):
    pass


@dataclass
class Eps(Grammar[Token]):
    trees: Lazy[List[AST]]


@dataclass
class Tok(Grammar[Token]):
    token: Token


@dataclass
class Seq(Grammar[Token]):
    children: List[Grammar[Token]]


@dataclass
class Alt(Grammar[Token]):
    children: List[Grammar[Token]]


@dataclass
class Red(Grammar[Token]):
    grammar: Grammar[Token]
    function: RedFunc


@dataclass
class Rep(Grammar[Token]):
    grammar: Grammar[Token]


@dataclass
class Ref(Grammar[Token]):
    rule: str
    grammar_dict: Dict[str, Grammar[Token]]


is_empty: Callable[[Grammar], bool] = fix(lambda: False, EqType.Eq)(match({
    Nil: lambda _:          True,
    Eps: lambda _, ts:      False,
    Tok: lambda _, t:       False,
    Seq: lambda _, gs:      any(map(is_empty, gs)),
    Alt: lambda _, gs:      all(map(is_empty, gs)),
    Red: lambda _, g, f:    is_empty(g),
    Rep: lambda _, g:       is_empty(g),
    Ref: lambda _, r, gd:   is_empty(gd[r]),
}, Grammar))


is_nullable: Callable[[Grammar], bool] = fix(lambda: True, EqType.Eq)(match({
    Nil: lambda _:          False,
    Eps: lambda _, ts:      True,
    Tok: lambda _, t:       False,
    Seq: lambda _, gs:      all(map(is_empty, gs)),
    Alt: lambda _, gs:      any(map(is_empty, gs)),
    Red: lambda _, g, f:    is_nullable(g),
    Rep: lambda _, g:       is_nullable(g),
    Ref: lambda _, r, gd:   is_nullable(gd[r]),
}, Grammar))


is_null: Callable[[Grammar], bool] = fix(lambda: True, EqType.Eq)(match({
    Nil: lambda _:          False,
    Eps: lambda _, ts:      True,
    Tok: lambda _, t:       False,
    Seq: lambda _, gs:      all(map(is_empty, gs)),
    Alt: lambda _, gs:      all(map(is_empty, gs)),
    Red: lambda _, g, f:    is_nullable(g),
    Rep: lambda _, g:       is_nullable(g),
    Ref: lambda _, r, gd:   is_nullable(gd[r]),
}, Grammar))


def parse_null_rep(g: Grammar) -> List[AST]:
    rep_parse = parse_null(g)
    if len(rep_parse) == 0:
        return [[]]
    return rep_parse


parse_null_func: Callable[[Grammar], List[AST]] = fix(list, EqType.Eq)(match({
    Nil: lambda _:          [],
    Eps: lambda _, ts:      ts,
    Tok: lambda _, t:       [],
    Seq: lambda _, gs:      foldr(list_product, [[]], list(map(parse_null, gs))),
    Alt: lambda _, gs:      concat(map(parse_null, gs)),
    Red: lambda _, g, f:    map(f, parse_null(g)),
    Rep: lambda _, g:       parse_null_rep(g),
    Ref: lambda _, r, gd:   parse_null(gd[r]),
}, Grammar))


def parse_null(g: Grammar) -> List[AST]:
    return parse_null_func(g)


def mk_eps_star(gs: List[Grammar]) -> Grammar:
    return Eps(cartesian_product(list(map(parse_null, gs))))


def mk_seq_star(prev_gs: List[Grammar], next_gs: List[Grammar]) -> Grammar:
    def f(tree: AST) -> AST:
        return tree
    return Red(Seq(cons(mk_eps_star(prev_gs), next_gs)), f)


def derive_seq(tok: Token, prev_gs: List[Grammar], next_gs: List[Grammar], accum_gs: List[Grammar]) -> List[Grammar]:
    if not next_gs:
        return accum_gs
    g, *next_gs_ = next_gs
    accum_gs_ = cons(mk_seq_star(prev_gs, cons(derive(g, tok), next_gs_), ), accum_gs)
    if is_nullable(g):
        return derive_seq(tok, snoc(prev_gs, g), next_gs_, accum_gs_)
    else:
        return accum_gs_


derive_func: Callable[[Grammar, Token], Grammar] = memoize(EqType.Eq, EqType.Equal)(match({
    Nil: lambda g, c:           Nil(),
    Eps: lambda g, c, _:        Nil(),
    Tok: lambda g, c, t:        Eps([t]) if t == c else Nil(),
    Seq: lambda g, c, gs:       Nil() if not gs else Alt(derive_seq(c, [], gs, [])),
    Alt: lambda g, c, gs:       Alt(list(map(lambda g_: derive(g_, c), gs))),
    Red: lambda g, c, g_, f:    Red(derive(g_, c), f),
    Rep: lambda g, c, g_:       Seq([derive(g_, c), g]),
    Ref: lambda g, c, r, gd:    derive(gd[r], c),
}, Grammar, ('g', 'c')))


def derive(g: Grammar, c: Token) -> Grammar:
    return derive_func(g, c)


"""
expr ::= term
       | expr '+' term
       | expr '-' term
term ::= factor
       | term '*' factor
       | term '/' factor
factor ::= DIGIT
         | '-' DIGIT
         | '(' expr ')'
         
###########

from derpgen.generate.pwd import *

d = {}

PLUS = Tok('+')
DASH = Tok('-')
STAR = Tok('*')
SLASH = Tok('/')
LPAR = Tok('(')
RPAR = Tok(')')
DIGIT = Tok('DIGIT')

expr = Ref('expr', d)
term = Ref('term', d)
factor = Ref('factor', d)

d['expr'] = Alt([term, Seq([expr, PLUS, term]), Seq([expr, DASH, term])])
d['term'] = Alt([factor, Seq([term, STAR, factor]), Seq([term, SLASH, factor])])
d['factor'] = Alt([DIGIT, Seq([DASH, DIGIT]), Seq([LPAR, expr, RPAR])])

s = d['expr']


"""
