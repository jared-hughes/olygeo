import scipy.optimize as opt
import numpy as np
from constructions import PrimitiveObject

class Problem:
    x0 = []
    constraints = []
    all_objects = {}
    # total number of degrees of freedom
    n = 0
    # object_names = ["B", "M", "circ"]
    object_names = []
    # object_dofs = [2, 2, 3]
    object_dofs = []
    # object_starts = [0, 2, 4]
    object_starts = [0]

    def _add_object(self, object_name, object_type, *vals):
        obj = PrimitiveObject(object_type, object_name, vals)
        self.all_objects[object_name] = obj
        return obj

    def add_fixed_object(self, object_name, object_type, *vals):
        return self._add_object(object_name, object_type, *vals)

    def add_param_object(self, object_name, object_type, *vals):
        self.object_names.append(object_name)
        dof = object_type.degrees_of_freedom()
        self.n += dof
        self.object_dofs.append(dof)
        last = self.object_starts[-1]
        self.object_starts.append(last + dof)
        self.x0 += vals
        return self._add_object(object_name, object_type, *vals)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def error(self):
        return sum(constraint.error(self.all_objects) \
            for constraint in self.constraints)

    def _error_vals(self, vals):
        for i, (start, length) in enumerate(zip(self.object_starts[:-1], self.object_dofs)):
            name = self.object_names[i]
            obj_vals = vals[start:start+length]
            self.all_objects[name].set_vals(obj_vals)
        return self.error()

    def _error_methods(self):
        constraints = []
        for constraint in self.constraints:
            constraints.append({
                "type": "ineq",
                "fun": lambda vals: constraint.error(self.all_objects)
            })
        return constraints

    def solve(self):
        x0 = np.reshape(self.x0, (self.n, 1))
        # tries to get `fun` as close to 0 as possible
        # while `constraints` are non-negative
        self.solution = opt.minimize(fun=self._error_vals, x0=x0, \
            method="COBYLA", constraints=self._error_methods()
        )

    def solution_points(self):
        if (self.solution is not None):
            return self.all_objects
        else:
            return None

if __name__ == "__main__":
    problem = Problem()
    problem.add_point("A")
    problem.add_point("B")
    problem.add_point("C")
    print(problem.solution())
