#!/usr/bin/env python3

def test_pygame():
    import olygeo.render.pygame
    p = olygeo.render.pygame.Pygame("pygame render", 640, 480)
    p.draw_point("A", 200, 250)
    p.draw_segment(50, 50, 200, 250)
    p.draw_circle(125, 150, 125)
    p.draw_circle(50, 50, 50)
    p.finish_drawing()

if __name__ == "__main__":
    test_pygame()
