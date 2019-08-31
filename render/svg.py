import drawSvg as draw
from .renderer import Renderer

class SVG(Renderer):
    def __init__(self, name, width, height):
        super().__init__(name, width, height)
        self.d = draw.Drawing(width, height)

    def _draw_segment(self, x1, y1, x2, y2):
        self.d.append(draw.Lines(x1, y1, x2, y2,
            stroke='black', stroke_width=self.EDGE_WEIGHT))

    def _draw_point(self, x, y):
        self.d.append(draw.Circle(x, y, self.POINT_RADIUS,
            fill='black', stroke='black', stroke_width=self.EDGE_WEIGHT))

    def _draw_circle(self, cx, cy, r):
        self.d.append(draw.Circle(cx, cy, r,
            fill='none', stroke='black', stroke_width=self.EDGE_WEIGHT))

    def _draw_label(self, label, x, y):
        self.d.append(draw.Text(label, self.LETTER_HEIGHT, x, y, center=True))

    def _finish_drawing(self):
        return self.d.asSvg()
