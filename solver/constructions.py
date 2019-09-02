from abc import ABC, abstractmethod
from .geometry import *
from .tools import distance, istypes, unsupported

__all__ = ["PrimitiveObject", "AbstractDependentConstruction",
           "SegmentConstruction", "MidpointConstruction"]

class AbstractConstruction(ABC):
    @abstractmethod
    def compute(self, points):
        pass

class PrimitiveObject(AbstractConstruction):
    def __init__(self, object_type, object_name, vals):
        self.object_type = object_type
        self.object_name = object_name
        self.vals = vals

    def set_vals(self, vals):
        self.vals = vals

    def compute(self, objects):
        # print("objs", objects)
        # print("osafjd", objects[self.object_name])
        return self.object_type(*self.vals)

    def __repr__(self):
        return f"PrimitiveObject({self.object_type.__name__}, {self.object_name}, {self.vals})"

class AbstractDependentConstruction(AbstractConstruction, ABC):
    def __init__(self, *objects):
        self.objects = objects

    def compute(self, points):
        objects = [object.compute(points) for object in self.objects]
        computed = self._compute(objects)
        if computed is not None:
            return computed
        else:
            unsupported(self, objects)

    @abstractmethod
    def _compute(self, objects):
        pass

class SegmentConstruction(AbstractDependentConstruction):
    def _compute(self, objects):
        if istypes(objects, [Point, Point]):
            return Line(*objects[0].pos, *objects[1].pos)

class MidpointConstruction(AbstractDependentConstruction):
    def _compute(self, objects):
        if istypes(objects, [Point, Point]):
            return Point((objects[0].pos + objects[1].pos)/2)
