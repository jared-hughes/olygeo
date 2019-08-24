from abc import ABC, abstractmethod
from geometry import Point

class AbstractConstruction(ABC):
    @abstractmethod
    def compute(self, points):
        pass

class PointFrom(AbstractConstruction):
    def __init__(self, point_name):
        self.point_name = point_name

    def compute(self, points):
        return Point(points[self.point_name])

class AbstractDependentConstruction(AbstractConstruction, ABC):
    def __init__(self, *objects):
        self.objects = objects

    def compute(self, points):
        objects = [object.compute(points) for object in self.objects]
        return self._compute(objects)

    @abstractmethod
    def _compute(self, objects):
        pass

class MidpointConstruction(AbstractDependentConstruction):
    def _compute(self, objects):
        if len(objects) == 2 and isinstance(objects[0], Point) and isinstance(objects[1], Point):
            return Point((objects[0].pos + objects[1].pos)/2)
        assert False, "Cannot take midpoint of these objects"
