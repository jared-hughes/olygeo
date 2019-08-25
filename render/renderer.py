from abc import ABC, abstractmethod
from enum import Enum

class Renderer(ABC):
    class Objects(Enum):
        SEGMENT = 1
        POINT = 2
        CIRCLE = 3

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.x_bound = None
        self.y_bound = None
        self.scene = []

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

    def draw_point(self, x, y):
        # assume negligable radius for scene sizing purposes
        self.expand_x(x)
        self.expand_y(y)
        self.scene.append((Renderer.Objects.POINT, x, y))

    def draw_circle(self, cx, cy, r):
        self.expand_x(cx - r)
        self.expand_x(cx + r)
        self.expand_y(cy - r)
        self.expand_y(cy + r)
        self.scene.append((Renderer.Objects.CIRCLE, cx, cy, r))

    def transform_length(self, length):
        return int(length * self.transform_scale)

    def transform_point(self, x, y):
        xp = self.transform_length(x - self.scene_center_x) + self.screen_center_x
        yp = self.transform_length(y - self.scene_center_y) + self.screen_center_y
        # should transform to large values where rounding is irrelevent
        return (int(xp), int(yp))

    def calculate_transforms(self):
        scene_width = self.x_bound[1] - self.x_bound[0]
        scene_height = self.y_bound[1] - self.y_bound[0]
        margin = 0.1
        margin_scale = 1 - 2*margin
        scale_w = margin_scale * self.width / scene_width
        scale_h = margin_scale * self.height / scene_height
        self.transform_scale = min(scale_w, scale_h)
        self.scene_center_x = scene_width/2 + self.x_bound[0]
        self.scene_center_y = scene_height/2 + self.y_bound[0]
        self.screen_center_x = self.width/2
        self.screen_center_y = self.height/2

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
            elif type == Renderer.Objects.POINT:
                # will get to labels later
                # have to scipy.optimize again to get closest point avoiding
                # surrounding lines + circles
                x, y = attrs
                x, y = self.transform_point(x, y)
                self._draw_point(x, y)
            elif type == Renderer.Objects.CIRCLE:
                cx, cy, r = attrs
                cx, cy = self.transform_point(cx, cy)
                r = self.transform_length(r)
                self._draw_circle(cx, cy, r)
            else:
                assert False, "Unknown Object"
        self._finish_drawing()

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
    def _finish_drawing(self):
        pass
