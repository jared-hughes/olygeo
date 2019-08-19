#!/usr/bin/python3
import lexer
import json
from enum import Enum

class Tags(Enum):
    WORD = "WORD"
    RESERVED = "RESERVED"
    PUNCT = "PUNCT"
    START = "START"
    END = "END"
    MATH = "MATH"
    MATH_COMPARE = "MATH_COMPARE"
    MATH_POINT = "MATH_POINT"
    MATH_OBJECT = "MATH_OBJECT"

class Modes(Enum):
    TEXT = "TEXT"
    MATH = "MATH"

def lex_string(string):
    """ Lex a string into words, math split by sentences """
    # assume no dollar signs in sentences
    text_token_exprs = [
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
    text_token_exprs += map(lambda k: (r"\b%s\b"%k, Tags.RESERVED), keywords)
    text_token_exprs += [
        (r'[,();!"#%&\'*+,-/:?@^_`{|}~]', Tags.PUNCT),
        (r'[a-zA-Z][a-z\-]*', Tags.WORD)
    ]
    math_token_exprs = [
        # Digits are almost always preceded by an underscore
        # A_0
        (r'[A-Z]\'?(_[a-z0-9])?', Tags.MATH_POINT, False),
        (r'[<>=]', Tags.MATH_COMPARE),
        # separate listing respectively
        (r',', Tags.PUNCT),
        # sometimes end a sentence inside math
        (r'\.', Tags.PUNCT),
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
    return lexer.lex(string, modes, Modes, Modes.TEXT, Tags.START, \
        Tags.END, case_insensitive=True)

def lex_case(case):
    return lex_string(case["content"])

def pp_lex(lex):
    """ Pretty-prints the lex in human-readable form """
    print("\n".join(map(lambda k: "\t".join(map(str, k)), lex)))

def ratio(success_count, attempt_count):
    success_ratio = success_count / attempt_count
    return "%d/%d=%d%%"%(success_count, attempt_count, int(success_ratio*100))

def test_math_lexing():
    import re
    with open("training_data/isl.json") as f:
        data = json.load(f)
    failures = []
    failure_count = 0
    success_count = 0
    case_success_count = 0
    case_total_count = len(data)
    for case in data:
        successful = True
        content = case["content"]
        math_expressions = re.findall("\$[^$]*\$", content)
        for expr in math_expressions:
            try:
                pp_lex(lex_string(expr))
                success_count += 1
            except:
                if successful:
                    print(":(", expr)
                successful = False
                failure_count += 1
                failures.append(expr)
        if successful:
            case_success_count += 1
    total_count = success_count + failure_count
    print("Failed expressions:\n", "\n".join(failures))
    print("Successful expressions: %s"%ratio(success_count, total_count))
    print("Successful cases: %s"%ratio(case_success_count, case_total_count))

if __name__ == '__main__':
    with open("training_data/isl.json") as data_file:
        data = json.load(data_file)
    pp_lex(lex_case(data[0]))
