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
        self._font(int(2*self.letter_radius))

    def _font(self, size):
        self.font = pygame.font.Font(None, size)

    def _draw_segment(self, x1, y1, x2, y2):
        pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2))

    def _draw_point(self, x, y):
        # use gfxdraw for AA?
        pygame.draw.circle(self.screen, BLACK, (x, y), 3)

    def _draw_circle(self, cx, cy, r):
        pygame.draw.circle(self.screen, BLACK, (cx, cy), r, 1)

    def _draw_label(self, label, x, y):
        # naively resize the font until the text_rect matches desired
        # height and width
        # probably slow
        text_rect = None
        length = len(label)
        font_size = self.letter_height
        while text_rect is None or (text_rect.height + 1 < self.letter_height \
        and text_rect.width < length * self.letter_width):
            text = self.font.render(label, True, BLACK)
            # centering: https://stackoverflow.com/a/39580531
            text_rect = text.get_rect(center=(x, y))
        # show a circle around the label
        # pygame.draw.circle(self.screen, (20, 140, 200), (x, y), int(self.letter_radius), 1)
        print(text_rect)
        self.screen.blit(text, text_rect)

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
