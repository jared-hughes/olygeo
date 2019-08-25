import numpy as np
from .geometry import Point

def distance(a, b):
    # point-to-point
    if isinstance(a, Point) and isinstance(b, Point):
        return np.linalg.norm(a.pos - b.pos)
    # number to None
    if b is None:
        return a
    raise TypeError(f"Distance is not defined on {type(a)} and {type(b)}")

def istypes(objects, permitted):
    if len(objects) != len(permitted):
        return False
    for object, permit in zip(objects, permitted):
        # print("O", type(object))
        # print("P", permit)
        if not isinstance(object, permit):
            return False
    return True

def unsupported(cls, objects):
    raise TypeError(f"Unsupported operand types for {type(cls).__name__}: "
        f"{[type(obj).__name__ for obj in objects]}")
