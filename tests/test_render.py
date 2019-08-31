#!/usr/bin/env python3

def test_renderer(r, name):
    p = r(name, 640, 480)
    p.draw_point("A", 200, 250)
    p.draw_segment(50, 50, 200, 250)
    p.draw_circle(125, 150, 125)
    p.draw_circle(50, 50, 50)
    return p.finish_drawing()

def test_pygame():
    from olygeo.render.pygame import Pygame
    test_renderer(Pygame, "Pygame render")

def test_svg():
    from olygeo.render.svg import SVG
    print(test_renderer(SVG, "SVG render"))

if __name__ == "__main__":
    # test_pygame()
    test_svg()
