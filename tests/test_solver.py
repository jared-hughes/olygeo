#!/usr/bin/env python3
from olygeo.solver.problem import Problem
from olygeo.solver.geometry import *
from olygeo.solver.constraints import *
from olygeo.solver.constructions import *

if __name__ == "__main__":
    problem = Problem()
    A = problem.add_fixed_object("A", Point, 0, 0)
    B = problem.add_param_object("B", Point)
    C = problem.add_fixed_object("C", Point, 5, 6)
    circ = problem.add_param_object("circ", Circle)
    # AB = CB
    problem.add_constraint(SameLengthConstraint(SegmentConstruction(A, B), SegmentConstruction(C, B)))
    # AB = 10
    problem.add_constraint(SameLengthConstraint(SegmentConstruction(A, B), Number(10)))
    problem.add_constraint(IntersectsConstraint(A, circ))
    problem.add_constraint(IntersectsConstraint(circ, B))
    problem.add_constraint(IntersectsConstraint(circ, C))
    problem.solve()
    print(problem.solution)
    print(problem.solution_points())
