# http://www.jayconrod.com/posts/37/a-simple-interpreter-from-scratch-in-python-part-1

import re
import sys

def lex(characters, token_exprs_raw, case_insensitive):
    pos = 0
    tokens = []
    # mod: compile everything first for my own sanity
    i = re.IGNORECASE if case_insensitive else 0
    def compile_expr(exp):
        return (re.compile(exp[0], i), exp[1], exp[2] if len(exp) > 2 else case_insensitive)
    token_exprs = list(map(compile_expr, token_exprs_raw))
    while pos < len(characters):
        match = None
        # try exprs, first one will override rest
        for expr in token_exprs:
            (regex, tag) = expr[:2]
            lower = case_insensitive
            if (len(expr) > 2):
                lower = expr[2]
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if lower:
                    text = text.lower()
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            # mod: custom error message
            nearby = characters[max(pos-10, 0):min(pos+10, len(characters))]
            error_text = "Illegal character at pos {}: {}\nNearby: {}".format(pos, characters[pos], nearby)
            raise ValueError(error_text)
        else:
            pos = match.end(0)
    return tokens
