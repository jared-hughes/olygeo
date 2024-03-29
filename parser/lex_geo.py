"""
The core module for tokenizing geometry problems.
"""
from .lexer import lex
import json
from enum import Enum
from .test import test

__all__ = ["lex_string", "all_keywords", "Tags"]

class Tags(Enum):
    """ Tags for Tokens """
    RESERVED = "RESERVED"
    START = "START"
    END = "END"
    MATH_COMPARE = "MATH_COMPARE"
    MATH_POINT = "MATH_POINT"
    MATH_OBJECT = "MATH_OBJECT"

class Modes(Enum):
    """ Different lexing modes """
    TEXT = "TEXT"
    MATH = "MATH"

keywords = [
    "let", "be", "a", "an", "the", "and",
    "quadrilateral", "triangle", "hexagon", "circle",
    "point", "points",
    "convex", "acute", "obtuse",
    "midpoint", "of",
    "passing through",
    "meets", "at"
]
""" All keywords with respect to lexing. Other plain words are ignored """

aux_reserved = [
    ".", ","
]
""" Auxilary list of reserved words in addition to keywords """

all_keywords = keywords + aux_reserved

def lex_string(string):
    """ Lex a geometry string into tokens, including math """
    # assume no dollar signs in sentences
    text_token_exprs = [
        # Ignore proposed by ...
        (r'Proposed by.*', None),
        # Ignore objectives
        (r'(Determine|Prove|Show|Find)[^\n]*\n',None),
        # Skip whitespace
        (r'\s', None),
        (r'\.', Tags.RESERVED),
        (r'\,', Tags.RESERVED),
    ]
    # not escaped, so don't use regex stuff
    # should only be letters anyway
    text_token_exprs += map(lambda k: (r"\b%s\b"%k, Tags.RESERVED), keywords)
    text_token_exprs += [
        # Ignore words
        (r'[a-zA-Z][a-z\-]*', None)
    ]
    math_token_exprs = [
        # Digits are almost always preceded by an underscore
        # A_0
        (r'[A-Z]\'?(_[a-z0-9])?', Tags.MATH_POINT, False),
        (r'[<>=]', Tags.MATH_COMPARE),
        # sometimes end a sentence inside math
        (r'\.', Tags.RESERVED),
        # separate listing respectively
        (r',', Tags.RESERVED),
        # \\Omega
        (r'\\[A-Za-z][a-z]*(_[a-z0-9])?', Tags.MATH_OBJECT, False),
        # Ignore curly braces because most functions are just monadic with the exception of frac
        (r'[{}]', None),
        # Skip whitespace
        (r'\s', None),
    ]
    modes = {
        Modes.TEXT: text_token_exprs + \
            [
                ("\$", Modes.MATH)
            ],
        Modes.MATH: math_token_exprs + \
            [
                ("\$", Modes.TEXT)
            ]
    }
    return lex(string, modes, Modes, Modes.TEXT, None, None, case_insensitive=True)

def lex_case(case):
    """ For testing, lex a single case """
    return lex_string(case["content"])

def pp_lex(lex):
    """ Pretty-prints a list of tokens in human-readable form """
    print("\n".join(map(lambda k: "\t".join(map(str, k)), lex)))

def test_math_lexing():
    """ Unit tests the lexing of math """
    import re
    def get_math(content):
        return re.findall("\$[^$]*\$", content)
    def pretty_lex(expr):
        pp_lex(lex_string(expr))
    test(pretty_lex, get_math)

    # Successful parts: 865/892=96%
    # Successful cases: 38/52=73%
