"""
Provides classes to create a hardcoded grammar to parse with

Modified from :ref:`parser-credits`.
"""
from math import inf
from collections import Sequence
from abc import ABC, abstractmethod

def sequencify(ls):
    """ Wrap any string or non-sequence into a list """
    # differentiate strings from OG sequences
    if isinstance(ls, Sequence) and not isinstance(ls, str):
        return ls
    else:
        return [ls]

def listify(ls):
    """ Wrap any non-list into a list """
    try:
        # should return ls unmodified if ls is a list
        return [] + ls
    except:
        return [ls]

class Result:
    """
    Result of a partial parse

    Parameters
    ----------
    value
        The captured value from the partial parse
    pos: int
        The number of characters parsed to get this result
    """
    def __init__(self, value, pos):
        self.value = value
        # index of next token in stream
        self.pos = pos

    def __repr__(self):
        return 'Result(\n%s\n%d)' % (indented(self.value), self.pos)


class IgnoredResult(Result):
    """ A Result that is ignored when Concat'd to something else """
    def __init__(self, pos):
        super().__init__(None, pos)

    def __repr__(self):
        return 'IgnoredResult(\n%d)' % (self.pos)

class ParserPair:
    """
    A pair of parsers

    Serves only to deal with left-associative __mul__ operator for Parser

    Parameters
    ----------
    left, right:
        The parsers
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __mul__(self, other):
        # hope other is function
        return Exp(self.left, self.right ^ (lambda x: other))

class Parser(ABC):
    """
    A parser that updates position when parsing and gives Results

    Notes
    -----
    Observe that combining operators follows operator preference
    https://docs.python.org/3/reference/expressions.html#operator-precedence,
    notably:

      1. ``|``: :class:`Alternate`
      2. ``^``: :class:`Process`
      3. ``+``: :class:`Concat`
      4. ``*``: :class:`Exp`
      5. ``**``: :class:`ExpSep`
    """

    @abstractmethod
    def __call__(self, tokens, pos):
        pass

    # applied when using + operator on two Parser objects
    def __add__(self, other):
        """ Concatenate two Parser objects together (+) """
        return Concat(self, other)

    # other needs to be Process (xored)
    def __mul__(self, other):
        """
        Create an Exp

        Notes
        -----
        This uses a triadic combination

            parser1() * separator() * cumulation_function()
        """
        if hasattr(other, "function"):
            # other is process
            return Exp(self, other)
        else:
            # hope other is parser
            # ParserPair is necessary due to left-associativity of * operator
            return ParserPair(self, other)

    def __pow__(self, other):
        """
        Create an ExpSep

        Notes
        -----
        This uses a triadic combination

            parser1() ** separator() ** cumulation_function()
        """
        if hasattr(other, "function"):
            # other is process
            return ExpSep(self, other.parser, other.function)
        if hasattr(self, "function"):
            # self is process, assume other is parser
            return ExpSep(self.parser, other, self.function)
        # assume other is function --> equivalent to ^
        return Process(self, other)

    def __or__(self, other):
        """ Take the Alternate of two Parser objects (|) """
        return Alternate(self, other)

    def __xor__(self, function):
        """ Take the Process of a Parser object and a function """
        if (function == 0):
            return Ignored(self)
        # list of elements separated by x
        return Process(self, function)

class Ignored(Parser):
    """
    A Parser which ignores returned results

    This only makes sense in the context of Concat, which will not append
    results from an Ignored.

    Parameters
    ----------
    parser: Parser
        the parser whose results are to be ignored
    """

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        IgnoredResult
            The result of the parser, except whose value is ignored
        """
        if self.parser(tokens, pos) is None:
            return None
        else:
            return IgnoredResult(pos+1)

class Reserved(Parser):
    """
    A Parser matching a specific value and tag

    Parameters
    ----------
    value: str
        The value from the lexer to be matched
    tag: :class:`olygeo.parser.lex_geo.Tags`
        The tag from the lexer to be matched
    """

    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        Result
            A result whose value is the string value of the token matched
        """
        if pos < len(tokens) and \
           tokens[pos][0] == self.value and \
           tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

class Tag(Parser):
    """
    A Parser matching a specific tag with any value

    Parameters
    ----------
    tag: :class:`lex_geo.Tags`
        The tag from the lexer to be matched
    """

    def __init__(self, tag):
        self.tag = tag

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        Result
            A result whose value is the string value of the token matched
        """
        if pos < len(tokens) and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

def signature(seq):
    """ The signature of a (nested) tuple for debugging """
    if isinstance(seq, tuple):
        parts = []
        for item in seq:
            parts += [signature(item)]
        return type(seq)(parts)
    else:
        return type(seq).__name__

    try:
        return "[%s]"%(", ".join(signature(item) for item in seq))
    except:
        return type(seq)

class Concat(Parser):
    """
    A Parser matching two parsers in a row.

    Equivalent to XY in regex

    Parameters
    ----------
    left, right: Parser
        The parsers on the left and the right to be concatenated together
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        Result
            The results of the left and right parsers appended to each other.
            This will return a single list, not a nested list based on
            associativity
        """
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                left = tuple(sequencify(left_result.value))
                right = tuple(sequencify(right_result.value))
                # combined_value = (*listify(left_result.value), right_result.value)
                combined_value = []
                if not isinstance(left_result, IgnoredResult):
                    combined_value += left
                if not isinstance(right_result, IgnoredResult):
                    combined_value += right
                return Result(combined_value, right_result.pos)
        return None

class Alternate(Parser):
    """
    A Parser matching either one parser or the other.

    Equivalent to X|Y in regex

    Parameters
    ----------
    left, right:
        The parsers, one of which must be matched for the Alternate to match
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        Result
            The result of the parser which matches, with the first parser
            taking precedence over the second.
        """
        left_result = self.left(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.right(tokens, pos)
            return right_result

class Opt(Parser):
    """
    A Parser matching 1 or 0 of a parser.

    Equivalent to X? in regex

    Parameters
    ----------
    parser: Parser
        The parser which may be matched
    """
    def __init__(self, parser, ignored_on_unmatch=False):
        self.parser = parser
        self.ignored_on_unmatch = ignored_on_unmatch

    def failure(self, pos):
        """
        Returns
        -------
        Result
            A Result with None value
        """
        return Result(None, pos)

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        Result
            The result of the parser if matched, or the result of :func:`failure`
            otherwise
        """
        result = self.parser(tokens, pos)
        if result:
            return result
        else:
            return self.failure(pos)

class IOpt(Opt):
    def failure(self, pos):
        """
        Returns
        -------
        IgnoredResult
            A Result that gets ignored in Concat
        """
        return IgnoredResult(pos)

class Rep(Parser):
    """
    A Parser that matches any number of another parser (including 0)

    Equivalent to X* in regex

    Parameters
    ----------
    parser: Parser
        The parser to be matches a number of times
    """
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        list of Result
            A list of all the results matched by parser
        """
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)

class RepMulti(Parser):
    """
    A Parser that matches another parser a number of times within a range

    Equivalent to X{min_reps, max_reps} in regex

    Parameters
    ----------
    parser: Parser
        The parser to be matches a number of times
    min_reps, max_reps: int
        The minimum and maximum number of repetitions, inclusive
    """
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
    """
    A Parser that applies a function to the Result of a parser

    Parameters
    ----------
    parser: Parser
        The parser to match
    function
        The function to be applied to the result
    """
    def __init__(self, parser, function):
        self.parser = parser
        self.function = function

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        Result
            function applied to the result of parser except when the result is
            None, at which point None is returned
        """
        result = self.parser(tokens, pos)
        if result:
            result.value = self.function(result.value)
            return result

class Lazy(Parser):
    """
    A Parser to delay generation of parser until runtime to allow recursion

    Parameters
    ----------
    parser_func
        A function that returns a parser to use
    """
    def __init__(self, parser_func):
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        The result of the parser from parser_func()
        """
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)

class Phrase(Parser):
    """
    A Parser that matches only when matching the full input stream of tokens

    Equivalent to X$ in regex

    Parameters
    ----------
    parser: Parser
        Parser to match fully
    """
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        The result of the parser if successful and its match lasts the full
        input stream, otherwise None
        """
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        else:
            return None

class Exp(Parser):
    """
    A Parser that matches another parser joined by a specific parser

    Equivalent to A(BA)* in regex but avoids left recursion

    Parameters
    ----------
    parser: Parser
        Main parser
    separator: Process
        Parser that matches token sequences that join the sequence.
        The function of separator should take left and right values and
        return a new value. A sane choice of function would be::

            lambda left, right: ListAST(left, right)
    """
    def __init__(self, parser, separator):
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        The result of the function from ``separator`` applied left to right
        across all matches of ``parser``
        """
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
    """
    A Parser that matches another parser joined by a specific parser

    Similar to Exp, but it also passes the matches of the separator into the
    joining function

    Equivalent to A(BA)* in regex but avoids left recursion

    Parameters
    ----------
    parser: Parser
        Main parser
    separator: Process
        Parser that matches token sequences that join the sequence.
        The function of separator should take left, sep, and right values and
        return a new value. A sane choice of function would be::

            lambda left, sep, right: ListAST(left, right, join=sep)
    """
    # list: A(BA)*
    def __init__(self, parser, separator, sepfunc):
        self.parser = parser
        self.separator = separator
        self.sepfunc = sepfunc

    def __call__(self, tokens, pos):
        """
        Returns
        -------
        The result of the function from ``separator`` applied left to right
        across all matches of ``parser`` and ``separator``
        """
        result = self.parser(tokens, pos)

        def process_next(parsed):
            (sep, right) = parsed
            print(sep)
            return self.sepfunc(result.value, sep, right)
        next_parser = self.separator + self.parser ^ process_next

        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result

class ZeroWidth(Parser):
    """
    A parser which always matches and just moves on with an empty match of None.

    This continues at the same position, so it does effectively nothing but is
    not ignored in Concat.

    This is effectively just for convenience.

    Warnings
    --------
    Only use at the end of an Alternate. Never repeat
    """
    def __call__(self, tokens, pos):
        return Result(None, pos)

def indented(string, amount=2, spacer=" ", sep="\n"):
    """
    Return a string indented at each line by a certain amount.

    By default, indents each line (determined by ``\\n`` linefeeds) by 2 spaces.
    """
    lines = str(string).split(sep)
    indented_lines = map(lambda line: spacer * amount + line, lines)
    return sep.join(indented_lines)

def star(f):
    """
    Convert a function to take a list of args instead of ``*args`` in sequence

    Notes
    -----
    See https://stackoverflow.com/q/21892989.
    """
    return lambda args: f(*args)
