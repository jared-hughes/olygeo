#!/usr/bin/env python3
from problem import Problem
from constraints import SamePointConstraint
from constructions import MidpointConstruction

problem = Problem()
A = problem.add_point("A", 0, 0, True)
B = problem.add_point("B", 10, 2)
C = problem.add_point("C", 5, 7, True)
problem.add_constraint(SamePointConstraint(MidpointConstruction(A, C), B))
problem.solve()
print(problem.solution_points())
