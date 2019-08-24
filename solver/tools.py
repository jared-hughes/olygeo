import numpy as np
from geometry import Point

def distance(a, b):
    # point-to-point
    if isinstance(a, Point) and isinstance(b, Point):
        return np.linalg.norm(a.pos - b.pos)
    # number to None
    if b is None:
        return a
    raise TypeError(f"Distance is not defined on {type(a)} and {type(b)}")
