from abc import ABC, abstractmethod

class AbstractObject(ABC):
    def compute(self, points):
        return self

class Number(AbstractObject):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"Number({self.val})"

    def length(self):
        return self.val

class Point:
    def __init__(self, pos):
        self.pos = pos

    def __repr__(self):
        return f"Point({self.pos[0]}, {self.pos[1]})"

class Line(AbstractObject):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return f"Segment({p1}, {p2})"

    def length(self):
        from tools import distance
        return distance(self.p1, self.p2)
