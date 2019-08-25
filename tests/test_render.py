#!/usr/bin/env python3

def test_pygame():
    import olygeo.render.pygame
    p = olygeo.render.pygame.Pygame("pygame render", 480, 640)
    p.draw_segment(50, 50, 200, 550)
    p.draw_point(400, 250)
    p.draw_circle(125, 150, 125)
    p.finish_drawing()

test_pygame()
