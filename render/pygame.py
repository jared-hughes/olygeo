import pygame
import sys
from .renderer import Renderer

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Pygame(Renderer):
    def __init__(self, name, width, height):
        super().__init__(name, width, height)
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(WHITE)
        self._font(int(2*self.LETTER_RADIUS))

    def _transform_point(self, x, y):
        """ override: reflect vertically to make y axis increase upward """
        return (x, 2 * self.scene_center_y - y)

    def _font(self, size):
        self.font = pygame.font.Font(None, size)

    def _draw_segment(self, x1, y1, x2, y2):
        pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), self.EDGE_WEIGHT)

    def _draw_point(self, x, y):
        # use gfxdraw for AA?
        pygame.draw.circle(self.screen, BLACK, (x, y), self.POINT_RADIUS)

    def _draw_circle(self, cx, cy, r):
        pygame.draw.circle(self.screen, BLACK, (cx, cy), r, self.EDGE_WEIGHT)

    def _draw_label(self, label, x, y):
        # naively resize the font until the text_rect matches desired
        # height and width
        # probably slow
        text_rect = None
        length = len(label)
        font_size = self.LETTER_HEIGHT
        while text_rect is None or (text_rect.height + 1 < self.LETTER_HEIGHT \
        and text_rect.width < length * self.LETTER_WIDTH):
            text = self.font.render(label, True, BLACK)
            # centering: https://stackoverflow.com/a/39580531
            text_rect = text.get_rect(center=(x, y))
        # show a circle around the label
        # pygame.draw.circle(self.screen, (20, 140, 200), (x, y), int(self.LETTER_RADIUS), 1)
        print(text_rect)
        self.screen.blit(text, text_rect)

    def _finish_drawing(self):
        pygame.display.update()
        while True:
           for event in pygame.event.get():
                if event.type == pygame.QUIT:
                     pygame.quit()
                     sys.exit()
