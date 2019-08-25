import pygame
import sys
from .renderer import Renderer

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Pygame(Renderer):
    def __init__(self, name, width, height):
        super().__init__(name, width, height)
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(WHITE)

    def _draw_segment(self, x1, y1, x2, y2):
        pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2))

    def _draw_point(self, x, y):
        # use gfxdraw for AA?
        pygame.draw.circle(self.screen, BLACK, (x, y), 3)

    def _draw_circle(self, cx, cy, r):
        pygame.draw.circle(self.screen, BLACK, (cx, cy), r, 1)

    def set_scale(self, min_x, min_y, max_x, max_y):
        pass

    def set_size(self, width, height):
        pass

    def _finish_drawing(self):
        pygame.display.update()
        while True:
           for event in pygame.event.get():
                if event.type == pygame.QUIT:
                     pygame.quit()
                     sys.exit()
