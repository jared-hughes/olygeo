# http://www.jayconrod.com/posts/37/a-simple-interpreter-from-scratch-in-python-part-1

import re
import sys

def lex(characters, modes, mode_types, start_mode, tag_start, tag_end, case_insensitive=False):
    pos = 0
    tokens = []
    # mod: compile everything first for my own sanity
    i = re.IGNORECASE if case_insensitive else 0
    def compile_expr(exp):
        return (re.compile(exp[0], i), exp[1], exp[2] if len(exp) > 2 else case_insensitive)
    # compile expressions
    modes = {mode: list(map(compile_expr, exprs)) for (mode, exprs) in modes.items()}
    mode = start_mode
    while pos < len(characters):
        match = None
        # try exprs, first one will override rest
        for expr in modes[mode]:
            (regex, tag) = expr[:2]
            lower = case_insensitive
            if (len(expr) > 2):
                lower = expr[2]
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if (len(text) == 0):
                    raise RuntimeError("Zero-length match with regex %s"%regex)
                if lower:
                    text = text.lower()
                if tag in mode_types:
                    # actually a transition
                    # tag is a mode
                    if tag_end is not None:
                        tokens.append((mode, tag_end))
                    mode = tag
                    if tag_start is not None:
                        tokens.append((mode, tag_start))
                elif tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            # mod: custom error message
            nearby = characters[max(pos-10, 0):min(pos+10, len(characters))]
            error_text = "Illegal character at pos %s: %s\n"%(pos, characters[pos]) \
                + "Nearby: %s\n"%nearby \
                + "Mode: %s"%mode
            raise ValueError(error_text)
        else:
            pos = match.end(0)
    return tokens
