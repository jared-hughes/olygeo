#!/usr/bin/env python3

from olygeo.backend.backend_wrappers import *
import olygeo.backend.spec_geo as sp

if __name__ == '__main__':
    # problem = """Let $ABC$ be an acute triangle and let $M$ be the midpoint of $AC$
    #   A circle $\\omega$ passing through $B$ and $M$ meets the sides $AB$ and $BC$ at points $P$ and $Q$ respectively
    #   Let $T$ be the point such that $BPTQ$ is a parallelogram
    #   Suppose that $T$ lies on the circumcircle of $ABC$
    #   Determine all possible values of $\\frac{BT}{BM}$."""
    problem = """Let $A$ be the midpoint of $BC$"""
    spec = problem_to_spec(problem)
    print(spec.to_json(indent=2))
    # print(sp.spec_types)
    # s = sp.Spec()
    # ps.params.append(sp.ParamPoint("A"))
    # json = s.to_json()
    # print(json)
    # print(sp.spec_from_json(json).to_json())
