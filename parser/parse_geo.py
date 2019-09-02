"""
The core module for parsing geometry as a sentence
"""
from .parser import *
from functools import reduce
from .lex_geo import *
import json
from .ast_geo import *

__all__ = ["parse"]

def print_pass(tag=None):
    """
    Return a function to Process a Parser with that acts as a print statement

    Use to print the value of a parser without affecting it

    Example
    ------
    >>> apply_parser((point() ^ print_pass("first point")) + point(), "$P$ $Q$")
    first point Point[P]
    Result(
      [Point[P], Point[Q]]
    2)
    """
    def _print_pass(x):
        if tag is None:
            print(x)
        else:
            print(tag, x)
        return x
    return _print_pass

def article():
    """ Return a parser for any article ('a', 'an', or 'the') """
    articles = ["a", "an", "the"]
    return any_keyword(articles)

def keyword(key):
    """
    Return a parser for a keyword

    Notes
    -----
    A keyword is any word that affects parsing. Other words outside math
    get ignored

    Raises
    ------
    AssertionError
        If key is not listed as a keyword in :py:mod:`olygeo.parser.lex_geo`
    """
    assert key in (all_keywords), "%s is not a keyword"%key
    return Reserved(key, Tags.RESERVED)

def point():
    """ Return a parser for a point """
    # most of the heavy lifting is done in the lexer
    return Tag(Tags.MATH_POINT) ^ Point

def segment():
    """
    Return a parser for a segment

    Notes
    -----
    A segment is two consecutive points.
    Segments are differentiated from distances by context
    """
    return point() + point() ^ star(Segment)

def distance():
    """
    Return a parser for a distance

    Notes
    -----
    A distance is two consecutive points.
    Segments are differentiated from distances by context
    """
    return point() + point() ^ star(Distance)

def compare_relation():
    """
    Return a parser for a compare relation

    Notes
    -----
    A compare relation is an inequality between two distances
    """
    comparison_op = any_of(["<",">","="], Tags.MATH_COMPARE)
    separator =  comparison_op
    sepfunc = lambda l, rel, r: CompareRelation(rel, l, r)
    return distance() ** separator ** sepfunc

def polygon():
    """
    Return a parser for any polygon

    Notes
    -----
    A polygon consists of 3 to 8 consecutive points
    """
    return RepMulti(point(), 3, 8) ^ Polygon

def obj():
    """ Return a parser for any object, such as $\\omega$ """
    return Tag(Tags.MATH_OBJECT) ^ Object

def reference():
    """
    Return a parser for an object reference.

    Notes
    -----
    A reference is any shape, possibly combined with an article, adjectives,
    or gerund adjectives
    """
    def process_reference(x):
        _, adj, ref, gerund = x
        print("sad al")
        adjs = adj.adj_list
        if gerund:
            adjs.append(gerund)
        all_adjs = AdjectiveList(adjs)
        return Reference(ref, all_adjs)

    return Opt(article()) + shape_adj_list() + (obj() | polygon() | segment() | point()) \
        + Opt(gerund_adj()) ^ process_reference

def multi(parser, singular=None, plural=None):
    """
    Return a parser for multiple of another parser.

    Parameters
    ----------
    parser:
        The parser that can be repeated.
    singular, plural:
        Singular and plural forms of the name of the object

    Examples
    --------
    >>> apply_parser(multi_point(), "$P$").value
    Multi[[Point[P]]]
    >>> apply_parser(multi_point(), "point $P$ and $Q$").value
    Multi[[Point[P], Point[Q]]]
    >>> apply_parser(multi_point(), "$P$, $Q$, and $R$").value
    Multi[[Point[P], Point[Q], Point[R]]]
    """
    prefix = ZeroWidth()
    if singular:
        prefix = singular | prefix
    if plural:
        prefix = plural | prefix
    return (prefix + ( \
            (parser() * keyword(",") * (lambda l, r: listify(l) + listify(r))) \
            + (Opt(IOpt(keyword(",")) + (keyword("and")^0) + parser()))
        )) \
        ^ print_pass("End") ^ (lambda x: Multi(x[1:]))

def multi_point():
    """ Return a parser for multiple of a point. """
    return multi(point, keyword("point"), keyword("points"))

def multi_reference():
    """ Return a parser for multiple of a reference. """
    return multi(reference)

def math():
    """ Return a parser for any math item. """
    return compare_relation() | reference()

def thing():
    """ Return a parser to match roughly anything: math or any reserved word. """
    # just testing a POC, so include everything
    return math() | Tag(Tags.RESERVED)

def any_of(words, tag):
    """ Return a parser for any token with a given tag and given value set. """
    def type(word):
        return Reserved(word, tag)
    word_parsers = map(type, words)
    return reduce(lambda l, r: l | r, word_parsers)

def any_keyword(words):
    """ Return a parser for any reserved word with value from a given set. """
    return any_of(words, Tags.RESERVED)

def midpoint():
    """ Return a parser for the relational adjective "midpoint." """
    return keyword("midpoint") + keyword("of") + segment() \
        ^ star(lambda _m, _o, segment: Adjective("midpoint", [segment]))

def relational_adj():
    """
    Return a parser for a relational adjective.

    Notes
    -----
    A relational adjective is an adjective that specifies a constraint on a
    shape given some other shapes
    """
    return midpoint()

def passing_through():
    """
    Return a parser for the gerund adjective "passing through".

    Notes
    -----
    The gerund adjective "passing through" specifies that the subject shape
    intersects the object shape at at least one point
    """

    return keyword("passing through") + multi_point() \
        ^ star(lambda _, obj: Relation("passing_through", obj))

def gerund_adj():
    """
    Return a parser for a gerund adjective.

    Notes
    -----
    A gerund adjective is an adjective ending in "-ing" that can be tacked
    on after a shape
    """
    return passing_through()

def meets():
    """
    Return a parser for the verb "meets."

    Notes
    -----
    The verb meets specifies that the subject shapes intersects its first object
    at its second object
    """
    def process_meets(x):
        _, refs, _, points = x
        return Verb("meets", [refs, points])
    # assume A meets B only at points
    return keyword("meets") + multi_reference() + keyword("at") + multi_point() \
        ^ process_meets

def verb():
    """ Return a parser for any verb, which can be used in a verb statement. """
    return meets()

def bool_adj():
    """ Return a parser for a boolean adjective that can describe a shape. """
    words = [
        "convex", "acute", "obtuse",
        # shapes are still boolean adjectives on sets of points
        "quadrilateral", "triangle", "hexagon", "circle"
    ]
    return any_keyword(words) ^ (lambda x: ObjectBoolAdj(x))

def shape_adj():
    """ Return a parser for a single adjective that can describe a shape. """
    return Opt(article()) + (relational_adj() | bool_adj()) \
        ^ star(lambda _, x: x)

def shape_adj_list():
    """ Return a parser for a list of adjectives that can describe a shape. """
    return Rep(shape_adj()) ^ print_pass("adj_list_meow") ^ (lambda x: AdjectiveList(x))

def let_statement():
    """
    Return a parser for a let statement.

    Notes
    -----
    A let statement has a single subject shape which receives one or more
    adjectives which specify constraints
    """
    return keyword("let") + reference() + keyword("be") + shape_adj_list() \
        ^ star(lambda _l, name, _b, adjs: Reference(name, adjs))

def verb_statement():
    """
    Return a parser for a verb statement.

    Notes
    -----
    A verb statement has a single subject shape which may act on any number of
    objects with a specific action
    """
    def process_verb_stmt(x):
        (ref, verb) = x
        return verb.add_noun(ref)
    return reference() + verb() ^ process_verb_stmt

def stmt():
    """
    Return a parser for a statement.

    Notes
    -----
    A statement directly specifies one or more constraints and can only be
    combined to AND components together
    """
    return let_statement() | verb_statement()

def sentence():
    """ Return a parser for a sentence. """
    return Rep(stmt() | thing()) ^ Sentence

def sentence_list():
    """ Return a parser for a list of sentences. """
    separator = keyword(".")
    join = (lambda l, r: SentenceList(l, r))
    return sentence() * separator * join

def geo_parser():
    """ Return a parser for sentences that spans the whole input token list. """
    return Phrase(sentence_list())

def parse(tokens):
    """
    Parse tokens from a geometry string.

    Parameters
    ---------
    tokens:
        the tokens to parse

    Returns
    -------
    AST
    """
    return geo_parser()(tokens, 0)

def test_math_parsing():
    """ Test the parsing of all math sequences """
    import re
    def get_math(content):
        return re.findall("\$[^$]*\$", content)
    def parse_math(string):
        tokens = lex_string(string)
        pp_lex(tokens)
        result = sentence()(tokens, 0)
        math_tags = [Tags.MATH_POINT, Tags.MATH_OBJECT, Tags.MATH_COMPARE]
        are_not_math_tags = map(lambda token: not(token in math_tags), tokens[result.pos:])
        assert result.pos == len(tokens) or all(are_math_tags)
        assert result != None
    test(parse_math, get_math)

def apply_parser(parser, string):
    """
    Parse a string with a specific parser

    Parameters
    ----------
    parser:
        the name of the parser to test
    string: str
        single string to tokenize and test

    Returns
    -------
    AST
    """
    tokens = lex_string(string)
    pp_lex(tokens)
    result = parser(tokens, 0)
    return result
