#!/usr/bin/env python3
from olygeo.parser.parse_geo import *

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
    # print(apply_parser(sentence, "A circle $\\omega$ passing through $B$ and $M$ meets the sides $AB$ and $BC$ at points $P$ and $Q$ respectively"))
    # print(apply_parser((point() ^ print_pass("first point")) + point(), "$P$ $Q$").value)
    # at $C$ and $D$
    print(apply_parser(compare_relation(), "$AB<CD=EF$").value)
    # test_math_parsing()
    # tokens = lex_string("$\\omega$")
    # pp_lex(tokens)
    # result = math()(tokens, 0)
    # print(result)
