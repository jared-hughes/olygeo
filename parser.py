# http://www.jayconrod.com/posts/38/a-simple-interpreter-from-scratch-in-python-part-2
from math import inf

class Result:
    def __init__(self, value, pos):
        self.value = value
        # index of next token in stream
        self.pos = pos

    def __repr__(self):
        return 'Result(\n%s\n%d)' % (indented(self.value), self.pos)

class ParserPair:
    """ Serves only to deal with left-associative __mul__ operator for Parser """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __mul__(self, other):
        # hope other is function
        return Exp(self.left, self.right ^ (lambda x: other))

class Parser:
    def __call__(self, tokens, pos):
        return None  # subclasses will override this

    # applied when using + operator on two Parser objects
    def __add__(self, other):
        return Concat(self, other)

    # other needs to be Process (xored)
    def __mul__(self, other):
        if hasattr(other, "function"):
            # other is process
            return Exp(self, other)
        else:
            # hope other is parser
            return ParserPair(self, other)

    def __pow__(self, other):
        if hasattr(other, "function"):
            # other is process
            return ExpSep(self, other.parser, other.function)
        if hasattr(self, "function"):
            # self is process, assume other is parser
            return ExpSep(self.parser, other, self.function)
        # assume other is function --> equivalent to ^
        return Process(self, other)

    def __or__(self, other):
        return Alternate(self, other)

    # ^
    # just a shortcut, not analagous to xor
    def __xor__(self, function):
        # list of elements separated by x
        return Process(self, function)

class Reserved(Parser):
    # specific value and tag, e.g. (".", Tags.FULLSTOP)
    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and \
           tokens[pos][0] == self.value and \
           tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

class Tag(Parser):
    # specific tag only, e.g. (*, Tags.WORD)
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

class Concat(Parser):
    # AB
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                combined_value = (left_result.value, right_result.value)
                return Result(combined_value, right_result.pos)
        return None

class Alternate(Parser):
    # A|B
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.right(tokens, pos)
            return right_result

class Opt(Parser):
    # A?
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            return result
        else:
            return Result(None, pos)

class Rep(Parser):
    # A*
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)

class RepMulti(Parser):
    # A{min_reps, max_reps}
    def __init__(self, parser, min_reps=1, max_reps=inf):
        self.parser = parser
        self.min_reps = min_reps
        self.max_reps = max_reps

    def __call__(self, tokens, pos):
        results = []
        result = self.parser(tokens, pos)
        for i in range(self.max_reps + 1):
            if result is None or i == self.max_reps:
                # finish up with conclusion
                if len(results) < self.min_reps:
                    return None
                else:
                    return Result(results, pos)
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)

class Process(Parser):
    # apply function to successful application of parser
    def __init__(self, parser, function):
        self.parser = parser
        self.function = function

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            result.value = self.function(result.value)
            return result

class Lazy(Parser):
    # delay generation of parser for recursion
    def __init__(self, parser_func):
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens, pos):
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)

class Phrase(Parser):
    # A$
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        else:
            return None

class Exp(Parser):
    # list: A(BA)*
    def __init__(self, parser, separator):
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)

        def process_next(parsed):
            (sepfunc, right) = parsed
            return sepfunc(result.value, right)
        next_parser = self.separator + self.parser ^ process_next

        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result

class ExpSep(Parser):
    """ Also passes the separator to the sepfunc """
    # list: A(BA)*
    def __init__(self, parser, separator, sepfunc):
        self.parser = parser
        self.separator = separator
        self.sepfunc = sepfunc

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)

        def process_next(parsed):
            (sep, right) = parsed
            print(sep)
            return self.sepfunc(sep, result.value, right)
        next_parser = self.separator + self.parser ^ process_next

        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result


def indented(string):
    amount = 2
    style = " "
    lines = str(string).split("\n")
    indented_lines = map(lambda line: style * amount + line, lines)
    return "\n".join(indented_lines)

# https://stackoverflow.com/q/21892989
def star(f):
  return lambda args: f(*args)
