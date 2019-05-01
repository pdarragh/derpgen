from .pwd import *

from derpgen.utility.match import *

from typing import Callable, TypeVar


Value = TypeVar('Value')

#
# def rep_red_func_branch(t: Branch[Value]) -> Tree[Value]:
#     ...
#
#
# rep_red_func: Callable[[Tree[Value]], Tree[Value]] = match({
#     Empty:  lambda t: t,
#     Leaf:   lambda t: t,
#     Branch: rep_red_func_branch,
# }, ('t',))


def optional_t(g: Grammar) -> Grammar:
    """
    Transforms g into an optional, i.e. g?.
    """
    return alt(g, eps([]))


def list_t(g: Grammar) -> Grammar:
    """
    Transforms g into a reduction over a list, i.e., w*.
    """
    return rep(g)


def nonempty_list_t(g: Grammar) -> Grammar:
    """
    Transforms g into a reduction over a nonempty list, i.e., w+.

    Constructed as:

          ◦
         / \
        w   *
            |
            w
    """
    return seq(g, list_t(g))


def separated_list_t(sep_g: Grammar, g: Grammar) -> Grammar:
    """
    Transforms g into a reduction over a separated list, e.g., w s w s w,
    where 'w' is the token to be matched and 's' is the separator to be
    discarded.

    Constructed as:

          ∪
         / \
        ε   ◦
           / \
          w   *
              |
              ◦
             / \
            s   w
    """
    return alt(eps([]), seq(g, rep(seq(sep_g, g))))


def nonempty_separated_list_t(sep_g: Grammar, g: Grammar) -> Grammar:
    """
    Transforms g into a reduction over a nonempty separated list. Similar to
    separated_list_t, but with at least one match.

    Constructed as:

        ◦
       / \
      w   *
          |
          ◦
         / \
        s   w
    """
    return seq(g, rep(seq(sep_g, g)))



