#!/usr/bin/python3
from parser import *
from functools import reduce
from lex_geo import *
import json
from ast_geo import *

def keyword(key):
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
    return obj() | polygon() | segment() | point()

def math():
    return compare_relation() | reference()

def thing():
    # just testing a POC, so include everything
    return math() | Tag(Tags.PUNCT) | Tag(Tags.RESERVED)

def any_of(words, tag):
    def type(word):
        return Reserved(word, tag)
    word_parsers = map(type, words)
    return reduce(lambda l, r: l | r, word_parsers)

def any_keyword(words):
    return any_of(words, Tags.RESERVED)

def midpoint():
    return keyword("midpoint") + keyword("of") + segment() \
        ^ star(lambda _, obj: Relation("midpoint", [obj]))

def relational_adj():
    return midpoint()

def bool_adj():
    words = [
        "convex", "acute", "obtuse",
        # shapes are still boolean adjectives on sets of points
        "quadrilateral", "triangle", "hexagon"
    ]
    return any_keyword(words) ^ (lambda x: ObjectBoolAdj(x))

def shape_adj():
    # ignore these
    articles = ["a", "an", "the"]
    return Opt(any_keyword(articles)) + (relational_adj() | bool_adj()) \
        ^ star(lambda _, x: x)

def shape_adj_list():
    return Rep(shape_adj()) ^ (lambda x: AdjectiveList(x))

def let_statement():
    def process_let(x):
        ((_, name), _), adjs = x
        return LetStatement(name, adjs)

    return keyword("let") + reference() + keyword("be") + shape_adj_list() \
        ^ process_let

def stmt():
    return let_statement()

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

if __name__ == '__main__':
    # with open("training_data/isl.json") as data_file:
    #     data = json.load(data_file)
    # tokens = lex_case(data[0])
    # result = parse_geo(tokens)
    # let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
    tokens = lex_string("""Let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
      A circle $\\omega$ passing through $B$ and $M$ meets the sides $AB$ and $BC$ at points $P$ and $Q$ respectively
      Let $T$ be the point such that $BPTQ$ is a parallelogram
      Suppose that $T$ lies on the circumcircle of $ABC$
      Determine all possible values of $\\frac{BT}{BM}$.""")
    pp_lex(tokens)
    result = parser()(tokens, 0)
    print(result)
    # test_math_parsing()
    # tokens = lex_string("$\\omega$")
    # pp_lex(tokens)
    # result = math()(tokens, 0)
    # print(result)
