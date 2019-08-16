#!/usr/bin/python3
import lexer
import json
from enum import Enum

class Tags(Enum):
    WORD = "WORD"
    MATH = "MATH"
    FULLSTOP = "FULLSTOP"
    PUNCT = "PUNCT"

def lex_string(string):
    """ Lex a string into words, math split by sentences """
    # assume no dollar signs in sentences
    token_exprs = [
        (r'\$[^$]*\$', Tags.MATH),
        # Ignore proposed by ...
        (r'Proposed by.*', None),
        # Skip whitespace
        (r'\s', None),
        (r'\.', Tags.FULLSTOP),
        (r'[,();!"#%&\'*+,-/:?@^_`{|}~]', Tags.PUNCT),
        (r'[a-zA-Z][a-z\-]*', Tags.WORD)
    ]
    return lexer.lex(string, token_exprs)

def lex_case(case):
    return lex_string(case["content"])

def pp_lex(lex):
    """ Pretty-prints the lex in human-readable form """
    print("\n".join(map(lambda k: "\t".join(map(str, k)), lex)))

with open("training_data/isl.json") as data_file:
    data = json.load(data_file)

pp_lex(lex_case(data[0]))
