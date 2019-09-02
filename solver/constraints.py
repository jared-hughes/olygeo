import numpy as np
from abc import ABC, abstractmethod
from .geometry import *
from .tools import distance, istypes, unsupported

__all__ = ["AbstractConstraint", "SamePointConstraint", "SameLengthConstraint",
           "IntersectsConstraint"]

class AbstractConstraint(ABC):
    def __init__(self, *objects):
        self.objects = objects

    # error should always be non-negative, trying to minimize it
    def error(self, objects):
        objects = [object.compute(objects) for object in self.objects]
        # squaring keeps non-negative and improves tendency to satisfy
        # all constraints well rather than a few poorly and others greatly
        err = self._error(objects)
        if err is not None:
            return err**2
        else:
            unsupported(self, objects)

    @abstractmethod
    def _error(self, points):
        pass

class SamePointConstraint(AbstractConstraint):
    def _error(self, objects):
        return distance(objects[0], objects[1])

class SameLengthConstraint(AbstractConstraint):
    def _error(self, objects):
        return objects[0].length() - objects[1].length()

class IntersectsConstraint(AbstractConstraint):
    def _error(self, objects):
        if istypes(objects, [Circle, Point]):
            return distance(objects[0].center, objects[1]) - objects[0].radius
        elif istypes(objects, [Point, Circle]):
            return self._error(objects[::-1])
