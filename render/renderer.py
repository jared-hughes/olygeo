from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
import scipy.optimize as opt

def _distance_point_point(x1, y1, x2, y2):
    return np.linalg.norm([x1 - x2, y1 - y2])

def _as_arrays(*x):
    assert len(x) % 2 == 0
    return list(map(np.asarray, zip(x[::2], x[1::2])))

def _distance_point_line(x, y, x1, y1, x2, y2):
    # https://stackoverflow.com/a/39840218
    # it's at this point that I regret using coordinates
    p, p1, p2 = _as_arrays(x, y, x1, y1, x2, y2)
    return np.abs(np.cross(p2-p1, p1-p))/np.linalg.norm(p2-p1)

def _distance_point_segment(x, y, x1, y1, x2, y2):
    p, p1, p2 = _as_arrays(x, y, x1, y1, x2, y2)
    # if obtuse
    if np.dot(p - p1, p2 - p1) < 0:
        return _distance_point_point(x, y, x1, y1)
    elif np.dot(p - p2, p1 - p2) < 0:
        return _distance_point_point(x, y, x2, y2)
    else:
        return _distance_point_line(x, y, x1, y1, x2, y2)

def _from_angle(theta):
    return np.asarray([np.cos(theta), np.sin(theta)])

class Renderer(ABC):
    class Objects(Enum):
        SEGMENT = 1
        POINT = 2
        CIRCLE = 3

    MARGIN_RATIO = 0.1
    LETTER_HEIGHT = 24
    LETTER_WIDTH = LETTER_HEIGHT
    LETTER_RADIUS = np.linalg.norm([LETTER_WIDTH, LETTER_HEIGHT])/2
    EDGE_WEIGHT = 1
    POINT_RADIUS = 3

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.x_bound = None
        self.y_bound = None
        self.scene = []
        self.transformed_objects = []
        self.labels = []

    @staticmethod
    def _expanded_bound(bound, a):
        if bound is None:
            return (a, a)
        else:
            if a < bound[0]:
                return (a, bound[1])
            elif a > bound[1]:
                return (bound[0], a)
            else:
                return bound

    def expand_x(self, x):
        self.x_bound = self._expanded_bound(self.x_bound, x)

    def expand_y(self, y):
        self.y_bound = self._expanded_bound(self.y_bound, y)

    def draw_segment(self, x1, y1, x2, y2):
        self.expand_x(x1)
        self.expand_x(x2)
        self.expand_y(y1)
        self.expand_y(y2)
        self.scene.append((Renderer.Objects.SEGMENT, x1, y1, x2, y2))

    def draw_point(self, label, x, y):
        # assume negligable radius for scene sizing purposes
        self.expand_x(x)
        self.expand_y(y)
        self.scene.append((Renderer.Objects.POINT, label, x, y))

    def draw_circle(self, cx, cy, r):
        self.expand_x(cx - r)
        self.expand_x(cx + r)
        self.expand_y(cy - r)
        self.expand_y(cy + r)
        self.scene.append((Renderer.Objects.CIRCLE, cx, cy, r))

    def transform_length(self, length):
        return int(length * self.transform_scale)

    def transform_point(self, x, y):
        x, y = self._transform_point(x, y)
        xp = self.transform_length(x - self.scene_center_x) + self.screen_center_x
        yp = self.transform_length(y - self.scene_center_y) + self.screen_center_y
        # should transform to large values where rounding doesn't matter
        return (int(xp), int(yp))

    def _transform_point(self, x, y):
        """ Implementing classes can override to perform a transformation """
        return (x, y)

    def calculate_transforms(self):
        scene_width = self.x_bound[1] - self.x_bound[0]
        scene_height = self.y_bound[1] - self.y_bound[0]
        margin_scale = 1 - 2*self.MARGIN_RATIO
        scale_w = margin_scale * self.width / scene_width
        scale_h = margin_scale * self.height / scene_height
        self.transform_scale = min(scale_w, scale_h)
        self.scene_center_x = scene_width/2 + self.x_bound[0]
        self.scene_center_y = scene_height/2 + self.y_bound[0]
        self.screen_center_x = self.width/2
        self.screen_center_y = self.height/2

    def place_label(self, label, preferred_x, preferred_y):
        length = len(label)
        width = length * self.LETTER_WIDTH
        height = self.LETTER_HEIGHT

        def error(xy):
            x, y = xy
            return np.linalg.norm([x - preferred_x, y - preferred_y])

        def constraints():
            out = []
            # 1 for each circle representing a letter
            for i in range(length):
                for constraint in letter_constraints(i):
                    out.append(constraint)
            return out

        def letter_constraints(i):
            out = []
            # 1 constraint for each other object
            for object in self.transformed_objects:
                type = object[0]
                attrs = object[1:]
                out.append(letter_object_constraint(i, type, attrs))
            return out

        # look at one letter as a circle
        def letter_object_constraint(i, type, attrs):
            def error(xy):
                x, y = xy
                r = self.LETTER_RADIUS
                cy = y
                cx = x - ((length-1)/2 - i) * r * 2
                if type == Renderer.Objects.SEGMENT:
                    x1, y1, x2, y2 = attrs
                    return _distance_point_segment(cx, cy, x1, y1, x2, y2) - r
                elif type == Renderer.Objects.POINT:
                    x1, y1 = attrs
                    return _distance_point_point(x, y, x1, y1) - r
                elif type == Renderer.Objects.CIRCLE:
                    cx1, cy1, r1 = attrs
                    # absolute value allow letters inside circles
                    return np.abs(_distance_point_point(cx, cy, cx1, cy1) - r1) - r
                    return err
            return {
                "type": "ineq",
                "fun": error
            }

        all_constraints = constraints()
        center_x0 = np.asarray([preferred_x, preferred_y], dtype=float)
        for displacement_size in range(1, 10, 2):
            for attempts in range(10):
                displacement = _from_angle(np.random.random() * np.pi * 2)
                # more fudge for longer words
                displacement *= displacement_size * length
                x0 = center_x0 + displacement
                solution = opt.minimize(fun=error, x0=x0, \
                    method="COBYLA", constraints=all_constraints
                )
                if solution.success: break
            if solution.success: break
        if solution.success:
            return solution.x
        else:
            return None

    def finish_drawing(self):
        self.calculate_transforms()

        for object in self.scene:
            type = object[0]
            attrs = object[1:]
            if type == Renderer.Objects.SEGMENT:
                x1, y1, x2, y2 = attrs
                x1, y1 = self.transform_point(x1, y1)
                x2, y2 = self.transform_point(x2, y2)
                self._draw_segment(x1, y1, x2, y2)
                self.transformed_objects.append((type, x1, y1, x2, y2))
            elif type == Renderer.Objects.POINT:
                label, x, y = attrs
                x, y = self.transform_point(x, y)
                self._draw_point(x, y)
                # do labels at end afer everything drawn in
                self.labels.append((label, x, y))
                self.transformed_objects.append((type, x, y))
            elif type == Renderer.Objects.CIRCLE:
                cx, cy, r = attrs
                cx, cy = self.transform_point(cx, cy)
                r = self.transform_length(r)
                self._draw_circle(cx, cy, r)
                self.transformed_objects.append((type, cx, cy, r))
            else:
                assert False, "Unknown Object"

        for label, preferred_x, preferred_y in self.labels:
            placement = self.place_label(label, preferred_x, preferred_y)
            if placement is not None:
                label_x, label_y = placement
                self._draw_label(label, int(label_x), int(label_y))
            else:
                print(f"Warning, could not place the label '{label}'")

        return self._finish_drawing()

    @abstractmethod
    def _draw_segment(self, x1, y1, x2, y2):
        pass

    @abstractmethod
    def _draw_point(self, x, y):
        pass

    @abstractmethod
    def _draw_circle(self, cx, cy, r):
        pass

    @abstractmethod
    def _draw_label(label, label_x, label_y):
        """ Implemented label methods should place labels within a LETTER_HEIGHT x
        len(label) * LETTER_WIDTH region centered at label_x, label_y"""
        pass

    @abstractmethod
    def _finish_drawing(self):
        pass
