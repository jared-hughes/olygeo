#!/usr/bin/env python3
from problem import Problem
from geometry import *
from constraints import *
from constructions import *

problem = Problem()
A = problem.add_point("A", 0, 0, True)
B = problem.add_point("B", 10, 3)
C = problem.add_point("C", 5, 0, True)
# AB = CB
problem.add_constraint(SameLengthConstraint(SegmentConstruction(A, B), SegmentConstruction(C, B)))
# AB = 10
problem.add_constraint(SameLengthConstraint(SegmentConstruction(A, B), Number(10)))
problem.solve()
print(problem.solution)
print(problem.solution_points())
