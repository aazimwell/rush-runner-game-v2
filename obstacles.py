"""Obstacle art. kinds: low (jump over), high (slide under), block (change lane)."""
import math

from kivy.graphics import Color, Ellipse, Line, Quad, Rectangle, RoundedRectangle


def draw_obstacle(kind, cx, by, u, t, a=1.0):
    """cx,by = bottom centre; u = pixel width of one lane at this depth; t = time (blink)."""
    if kind == 'low':
        w, h = .84 * u, .50 * u
        Color(0.05, 0.05, 0.1, a)
        Rectangle(pos=(cx - .36 * u, by), size=(.07 * u, .20 * u))
        Rectangle(pos=(cx + .29 * u, by), size=(.07 * u, .20 * u))
        Color(1.0, 0.82, 0.1, a)
        RoundedRectangle(pos=(cx - w / 2, by + .18 * u), size=(w, h * .62), radius=[.04 * u])
        Color(0.05, 0.05, 0.08, a)
        n = 6
        sw = w / n
        for i in range(0, n, 2):
            x0 = cx - w / 2 + i * sw
            Quad(points=[x0, by + .18 * u, x0 + sw * .6, by + .18 * u, x0 + sw * 1.0, by + .18 * u + h * .62, x0 + sw * .4, by + .18 * u + h * .62])
        Color(1.0, 0.3, 0.2, a * (0.5 + 0.5 * (math.sin(t * 9) > 0)))
        Ellipse(pos=(cx - .06 * u, by + .52 * u), size=(.12 * u, .12 * u))
    elif kind == 'high':
        Color(0.06, 0.10, 0.30, a)
        Rectangle(pos=(cx - .46 * u, by), size=(.07 * u, 1.45 * u))
        Rectangle(pos=(cx + .39 * u, by), size=(.07 * u, 1.45 * u))
        Color(0.2, 0.8, 1.0, a)
        Line(rectangle=(cx - .46 * u, by, .07 * u, 1.45 * u), width=1.2)
        Line(rectangle=(cx + .39 * u, by, .07 * u, 1.45 * u), width=1.2)
        Color(1.0, 0.2, 0.7, a * .25)
        RoundedRectangle(pos=(cx - .50 * u, by + .88 * u), size=(1.0 * u, .42 * u), radius=[.05 * u])
        Color(1.0, 0.25, 0.75, a)
        RoundedRectangle(pos=(cx - .46 * u, by + .95 * u), size=(.92 * u, .28 * u), radius=[.04 * u])
        Color(1, 1, 1, a * .8)
        Rectangle(pos=(cx - .43 * u, by + 1.15 * u), size=(.86 * u, .03 * u))
    else:
        Color(0.0, 0.0, 0.0, a * .35)
        Ellipse(pos=(cx - .46 * u, by - .05 * u), size=(.92 * u, .12 * u))
        Color(0.10, 0.12, 0.34, a)
        RoundedRectangle(pos=(cx - .42 * u, by + .05 * u), size=(.84 * u, 1.55 * u), radius=[.08 * u])
        Color(0.18, 0.22, 0.52, a)
        RoundedRectangle(pos=(cx - .42 * u, by + .75 * u), size=(.84 * u, .85 * u), radius=[.08 * u])
        Color(0.55, 0.95, 1.0, a)
        RoundedRectangle(pos=(cx - .32 * u, by + 1.08 * u), size=(.64 * u, .36 * u), radius=[.05 * u])
        Color(0.2, 0.8, 1.0, a)
        Line(rounded_rectangle=(cx - .42 * u, by + .05 * u, .84 * u, 1.55 * u, .08 * u), width=1.4)
        Color(1.0, 0.25, 0.7, a)
        Rectangle(pos=(cx - .40 * u, by + .62 * u), size=(.80 * u, .045 * u))
        Color(1.0, 0.9, 0.5, a)
        Ellipse(pos=(cx - .34 * u, by + .20 * u), size=(.14 * u, .10 * u))
        Ellipse(pos=(cx + .20 * u, by + .20 * u), size=(.14 * u, .10 * u))
