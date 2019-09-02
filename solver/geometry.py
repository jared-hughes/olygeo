from abc import ABC, abstractmethod, abstractproperty
import numpy as np
from ..parser.parser import *

__all__ = ["AbstractObject", "Number", "Point", "Circle", "Line"]

class AbstractObject(ABC):
    def __init__(self, *vals):
        # print(vals, self.__class__.degrees_of_freedom())
        assert len(vals) == self.__class__.degrees_of_freedom()
        self.vals = vals
        self.assign_props()

    def compute(self, points):
        return self

    @abstractmethod
    def assign_props(self):
        pass

    @abstractproperty
    def degrees_of_freedom():
        pass

class Number(AbstractObject):
    def assign_props(self):
        self.val = self.vals[0]

    def __repr__(self):
        return f"Number({self.val})"

    def degrees_of_freedom():
        return 1

    def length(self):
        return self.val

class Point(AbstractObject):
    def assign_props(self):
        self.pos = np.array(self.vals)

    def __repr__(self):
        return f"Point({self.pos[0]}, {self.pos[1]})"

    def degrees_of_freedom():
        return 2

class Circle(AbstractObject):
    def assign_props(self):
        self.center = Point(*self.vals[0:2])
        self.radius = self.vals[2]

    def __repr__(self):
        return f"Circle({self.center}, {self.radius})"

    def degrees_of_freedom():
        return 3

class Line(AbstractObject):
    def assign_props(self):
        self.p1 = Point(*self.vals[0:2])
        self.p2 = Point(*self.vals[2:4])

    def __repr__(self):
        return f"Segment({self.p1}, {self.p2})"

    def length(self):
        from .tools import distance
        return distance(self.p1, self.p2)

    def degrees_of_freedom():
        return 4
