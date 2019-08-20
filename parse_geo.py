#!/usr/bin/python3
from parser import *
from functools import reduce
from lex_geo import *
import json
from ast_geo import *

def keyword(key):
    return Reserved(key, Tags.RESERVED)

def point():
    return Tag(Tags.MATH_POINT)

def polygon():
    return RepPlus(point())

def obj():
    return Tag(Tags.MATH_OBJECT)

def reference():
    return obj() | polygon()

def math():
    return reference()

def thing():
    # just testing a POC, so include everything
    return math() | Tag(Tags.PUNCT)

def any_keyword(words):
    word_parsers = map(keyword, words)
    return reduce(lambda l, r: l | r, word_parsers)

def midpoint():
    return keyword("midpoint") + keyword("of") + Tag(Tags.MATH) \
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

    return keyword("let") + Tag(Tags.MATH) + keyword("be") + shape_adj_list() \
        ^ process_let

def stmt():
    return let_statement()

def sentence():
    return Rep(stmt() | thing()) ^ Sentence

def sentence_list():
    separator = keyword(".") ^ (lambda x: lambda l, r: SentenceList(l, r))
    return sentence() * separator

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
        result = math()(tokens, 0)
        assert result.pos == len(tokens)
        assert result != None
    test(parse_math, get_math)

if __name__ == '__main__':
    # with open("training_data/isl.json") as data_file:
    #     data = json.load(data_file)
    # tokens = lex_case(data[0])
    # result = parse_geo(tokens)
    # let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
    # tokens = lex_string("""Let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
    #   A circle $\\omega$ passing through $B$ and $M$ meets the sides $AB$ and $BC$ at points $P$ and $Q$ respectively
    #   Let $T$ be the point such that $BPTQ$ is a parallelogram
    #   Suppose that $T$ lies on the circumcircle of $ABC$
    #   Determine all possible values of $\\frac{BT}{BM}$.""")
    # pp_lex(tokens)
    # result = sentence()(tokens, 0)
    # print(result)
    test_math_parsing()
    # tokens = lex_string("$\\omega$")
    # pp_lex(tokens)
    # result = math()(tokens, 0)
    # print(result)
