#!/usr/bin/python3
from parser import *
from functools import reduce
from lex_geo import *
import json

class SentenceList:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s\n%s"%(self.left, self.right)

class Sentence:
    def __init__(self, things):
        self.things = things

    def __repr__(self):
        return "Sentence\n%s"%(indented(self.things))

class Statement:
    pass

class LetStatement(Statement):
    def __init__(self, name, object):
        self.name = name
        self.object = object

    def __repr__(self):
        return "Let[%s, %s]"%(self.name, self.object)

class ObjectBoolAdj:
    def __init__(self, adj):
        self.adj = adj

    def __repr__(self):
        return "BoolAdj[%s]"%self.adj

class AdjectiveList:
    def __init__(self, adj_list):
        self.adj_list = adj_list

    def __repr__(self):
        return "AdjList[%s]"%(self.adj_list)

class Relation:
    def __init__(self, rel, objects):
        self.rel = rel
        self.objects = objects

    def __repr__(self):
        return "Relation[%s, %s]"%(self.rel, self.objects)

class Construction:
    def __init__(self, rel, from_objects):
        self.rel = rel
        self.from_objects = from_objects

    def __repr__(self):
        return "Construction[%s, %s]"%(self.rel, self.from_objects)


def keyword(key):
    return Reserved(key, Tags.RESERVED)

def thing():
    # just testing a POC, so include everything
    return Tag(Tags.WORD) | Tag(Tags.MATH) | Tag(Tags.PUNCT)

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

if __name__ == '__main__':
    with open("training_data/isl.json") as data_file:
        data = json.load(data_file)
    # tokens = lex_case(data[0])
    # result = parse_geo(tokens)
    # let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
    tokens = lex_string("let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$")
    pp_lex(tokens)
    result = sentence()(tokens, 0)
    print(result)
