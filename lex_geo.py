#!/usr/bin/python3
import lexer
import json
from enum import Enum

class Tags(Enum):
    WORD = "WORD"
    MATH = "MATH"
    RESERVED = "RESERVED"
    PUNCT = "PUNCT"

def lex_string(string):
    """ Lex a string into words, math split by sentences """
    # assume no dollar signs in sentences
    token_exprs = [
        (r'\$[^$]*\$', Tags.MATH, False),
        # Ignore proposed by ...
        (r'Proposed by.*', None),
        # Skip whitespace
        (r'\s', None),
        (r'\.', Tags.RESERVED),
    ]
    # not escaped, so don't use regex stuff
    # should only be letters anyway
    keywords = [
        "let", "be", "a", "an", "the",
        "quadrilateral", "triangle", "hexagon",
        "convex", "acute", "obtuse",
        "midpoint", "of"
    ]
    token_exprs += map(lambda k: (r"\b%s\b"%k, Tags.RESERVED), keywords)
    token_exprs += [
        (r'[,();!"#%&\'*+,-/:?@^_`{|}~]', Tags.PUNCT),
        (r'[a-zA-Z][a-z\-]*', Tags.WORD)
    ]
    return lexer.lex(string, token_exprs, True)

def lex_case(case):
    return lex_string(case["content"])

def pp_lex(lex):
    """ Pretty-prints the lex in human-readable form """
    print("\n".join(map(lambda k: "\t".join(map(str, k)), lex)))

if __name__ == '__main__':
    with open("training_data/isl.json") as data_file:
        data = json.load(data_file)
    pp_lex(lex_case(data[0]))
