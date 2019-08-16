# http://www.jayconrod.com/posts/37/a-simple-interpreter-from-scratch-in-python-part-1

import re
import sys

def lex(characters, token_exprs_raw):
    pos = 0
    tokens = []
    # mod: compile everything first for my own sanity
    print(token_exprs_raw)
    token_exprs = list(map(lambda exp: (re.compile(exp[0]), exp[1]), token_exprs_raw))
    while pos < len(characters):
        match = None
        # try exprs, first one will override rest
        for regex, tag in token_exprs:
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
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
