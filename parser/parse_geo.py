#!/usr/bin/python3
from parser import *
from functools import reduce
from lex_geo import *
import json
from ast_geo import *

def print_pass(tag):
    def _print_pass(x):
        print(tag, x)
        return x
    return _print_pass

def article():
    articles = ["a", "an", "the"]
    return any_keyword(articles)

def keyword(key):
    assert key in (keywords + aux_reserved), "%s is not a keyword"%key
    return Reserved(key, Tags.RESERVED)

def point():
    return Tag(Tags.MATH_POINT) ^ Point

def segment():
    return point() + point() ^ star(Segment)

def distance():
    return point() + point() ^ star(Distance)

def compare_relation():
    comparison_op = any_of(["<",">","="], Tags.MATH_COMPARE)
    separator =  comparison_op
    sepfunc = lambda l, m, r: CompareRelation(l, m, r)
    return distance() ** separator ** sepfunc

def polygon():
    return RepMulti(point(), 3, 8) ^ Polygon

def obj():
    return Tag(Tags.MATH_OBJECT) ^ Object

def reference():
    def process_reference(x):
        _, adj, ref, gerund = x
        all_adjs = AdjectiveList(adj.adj_list + [gerund])
        return Reference(ref, all_adjs)

    return Opt(article()) + shape_adj_list() + (obj() | polygon() | segment() | point()) \
        + Opt(gerund_adj()) ^ process_reference

def multi(parser, singular=None, plural=None):
    """ multi(point(), keyword("point"), keyword("points")) --> "point P", "P", "points P and Q" """
    def process_and(x):
        print(x)
        return x[0:-3] + x[-1:]
    prefix = ZeroWidth()
    if singular:
        prefix = singular | prefix
    if plural:
        prefix = plural | prefix
    print("PRE", prefix)
    return (prefix + ( \
            ((parser() * keyword(",") * (lambda l, r: listify(l) + listify(r))) \
            + Opt(Opt(keyword(",")) + keyword("and") + parser()) ^ process_and)
        )) \
        ^ print_pass("pre") ^ (lambda x: Multi(x[1:]))

def multi_point():
    return multi(point, keyword("point"), keyword("points"))

def multi_reference():
    return multi(reference)

def math():
    return compare_relation() | reference()

def thing():
    # just testing a POC, so include everything
    return math() | Tag(Tags.RESERVED)

def any_of(words, tag):
    def type(word):
        return Reserved(word, tag)
    word_parsers = map(type, words)
    return reduce(lambda l, r: l | r, word_parsers)

def any_keyword(words):
    return any_of(words, Tags.RESERVED)

def midpoint():
    return keyword("midpoint") + keyword("of") + segment() \
        ^ star(lambda _m, _o, segment: Relation("midpoint", [segment]))

def relational_adj():
    return midpoint()

def passing_through():
    return keyword("passing through") + multi_point() \
        ^ star(lambda _, obj: Relation("passing_through", obj))

def gerund_adj():
    return passing_through()

def meets():
    def process_meets(x):
        _, refs, _, points = x
        return Verb("meets", [refs, points])
    # assume A meets B only at points
    return keyword("meets") + multi_reference() + keyword("at") + multi_point() \
        ^ process_meets

def verb():
    return meets()

def bool_adj():
    words = [
        "convex", "acute", "obtuse",
        # shapes are still boolean adjectives on sets of points
        "quadrilateral", "triangle", "hexagon", "circle"
    ]
    return any_keyword(words) ^ (lambda x: ObjectBoolAdj(x))

def shape_adj():
    return Opt(article()) + (relational_adj() | bool_adj()) \
        ^ star(lambda _, x: x)

def shape_adj_list():
    return Rep(shape_adj()) ^ (lambda x: AdjectiveList(x))

def let_statement():
    return keyword("let") + reference() + keyword("be") + shape_adj_list() \
        ^ star(lambda _l, name, _b, adjs: Reference(name, adjs))

def verb_statement():
    def process_verb_stmt(x):
        (ref, verb) = x
        return verb.add_noun(ref)
    return reference() + verb() ^ process_verb_stmt

def stmt():
    return let_statement() | verb_statement()

def sentence():
    return Rep(stmt() | thing()) ^ Sentence

def sentence_list():
    separator = keyword(".")
    join = (lambda l, r: SentenceList(l, r))
    return sentence() * separator * join

def parser():
    return Phrase(sentence_list())

def parse_geo(tokens):
    return parser()(tokens, 0)

def test_math_parsing():
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

def test(parser, string):
    tokens = lex_string(string)
    pp_lex(tokens)
    result = parser()(tokens, 0)
    print(result)

if __name__ == '__main__':
    # with open("data/training/isl.json") as data_file:
    #     data = json.load(data_file)
    # tokens = lex_case(data[0])
    # result = parse_geo(tokens)
    # let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
    # test(parser, """A circle $\\omega$ passing through $B$ and $M$ meets the sides $AB$ and $BC$ at points $P$ and $Q$ respectively
    #   Let $T$ be the point such that $BPTQ$ is a parallelogram
    #   Suppose that $T$ lies on the circumcircle of $ABC$
    #   Determine all possible values of $\\frac{BT}{BM}$.""")
    test(sentence, "A circle $\\omega$ passing through $B$ and $M$ meets the sides $AB$ and $BC$ at points $P$ and $Q$ respectively")
    # test_math_parsing()
    # tokens = lex_string("$\\omega$")
    # pp_lex(tokens)
    # result = math()(tokens, 0)
    # print(result)
