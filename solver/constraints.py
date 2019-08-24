import numpy as np
from abc import ABC, abstractmethod
from geometry import Point
from tools import distance

class AbstractConstraint(ABC):
    def __init__(self, *objects):
        self.objects = objects

    def error(self, points):
        objects = [object.compute(points) for object in self.objects]
        return self._error(objects)

    @abstractmethod
    def _error(self, points):
        pass

class SamePointConstraint(AbstractConstraint):
    def _error(self, objects):
        return distance(objects[0], objects[1])
