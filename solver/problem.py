import scipy.optimize as opt
import numpy as np
from constructions import PointFrom

class Problem:
    x0 = []
    constraints = []
    all_points = {}
    # id --> non-fixed point name
    point_names = []
    n = 0

    def add_point(self, point_name, x, y, fixed=False):
        pos = np.array([x, y])
        if not fixed:
            self.point_names.append(point_name)
            self.n += 1
            self.x0.append(pos)
        self.all_points[point_name] = pos
        return PointFrom(point_name)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def error(self):
        return sum(constraint.error(self.all_points) \
            for constraint in self.constraints)

    def _error_vals(self, vals):
        points = np.reshape(vals, (self.n, 2))
        for i, point in enumerate(points):
            name = self.point_names[i]
            self.all_points[name] = point
        return self.error()

    def _error_methods(self):
        constraints = []
        for constraint in self.constraints:
            constraints.append({
                "type": "ineq",
                "fun": lambda vals: constraint.error(self.all_points)
            })
        return constraints

    def solve(self):
        x0 = np.reshape(self.x0, (2*self.n, 1))
        # tries to get `fun` as close to 0 as possible
        # while `constraints` are non-negative
        self.solution = opt.minimize(fun=self._error_vals, x0=x0, \
            method="COBYLA", constraints=self._error_methods()
        )

    def solution_points(self):
        if (self.solution is not None):
            return self.all_points
        else:
            return None

if __name__ == "__main__":
    problem = Problem()
    problem.add_point("A")
    problem.add_point("B")
    problem.add_point("C")
    print(problem.solution())
