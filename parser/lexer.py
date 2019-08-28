"""
Provides a single function to tokenize based on a given grammar.

Modified from :ref:`parser-credits`.
"""

import re
import sys

def lex(characters, modes, mode_types, start_mode, tag_start, tag_end, case_insensitive=False):
    """
    Tokenize a string

    Parameters
    ----------
    characters: str | list of chars
        The string to tokenize
    modes:
        Main specification of the grammar

        Should be a dictionary from modes to lists of pairs ``(regex, effect)``
        such as ::

            {
                mode_1: [
                    (regex_1, tag_1),
                    (regex_2, tag_2),
                    (regex_3, mode_1)
                ],
                mode_2: [ ... ]
            }

        If ``effect`` is a member of mode_types, such as with ``(regex_3, mode_1)``
        here, the mode transitions to to the mode.
        Otherwise a token emitted with the matched text and the given tag.
    """
    pos = 0
    tokens = []
    # mod: compile everything first for my own sanity
    i = re.IGNORECASE if case_insensitive else 0
    # always do MULTILINE to match newlines
    i = i | re.MULTILINE
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
