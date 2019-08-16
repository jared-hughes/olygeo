#!/usr/bin/python3
from parser import *
from lex_geo import Tags, lex_case
import json

class SentenceList:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "SentenceList(%s, %s)"%(self.left, self.right)

class Sentence:
    def __init__(self, things):
        self.things = things

    def __repr__(self):
        return "Sentence(%s)"%(self.things)

def keyword(key):
    return Reserved(key, Tags.RESERVED)

def thing():
    # just testing a POC, so just include everything
    return Tag(Tags.WORD) | Tag(Tags.MATH) | Tag(Tags.PUNCT)

def sentence():
    return Rep(thing()) ^ Sentence

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
    tokens = lex_case(data[0])
    result = parse_geo(tokens)
    print(result)
