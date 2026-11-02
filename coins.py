"""Collectible art: spinning gold coin and blue diamond."""
import math

from kivy.graphics import Color, Ellipse, Line, Quad, Triangle


def draw_coin(cx, cy, r, spin, a=1.0):
    wd = max(r * .16, r * abs(math.cos(spin)))
    Color(1.0, 0.72, 0.05, a * .35)
    Ellipse(pos=(cx - wd * 1.35, cy - r * 1.3), size=(wd * 2.7, r * 2.6))
    Color(1.0, 0.80, 0.12, a)
    Ellipse(pos=(cx - wd, cy - r), size=(wd * 2, r * 2))
    Color(0.85, 0.50, 0.04, a)
    Line(ellipse=(cx - wd * .68, cy - r * .68, wd * 1.36, r * 1.36), width=max(1.0, r * .09))
    Color(1, 1, .8, a * .8)
    Ellipse(pos=(cx - wd * .55, cy + r * .15), size=(wd * .30, r * .40))


def draw_diamond(cx, cy, r, spin, a=1.0):
    wd = max(r * .35, r * abs(math.cos(spin)))
    Color(.2, .7, 1, a * .3)
    Ellipse(pos=(cx - wd * 1.5, cy - r * 1.4), size=(wd * 3, r * 2.8))
    Color(.15, .65, 1.0, a)
    Quad(points=[cx - wd, cy + r * .2, cx - wd * .5, cy + r, cx + wd * .5, cy + r, cx + wd, cy + r * .2])
    Color(.05, .42, .9, a)
    Triangle(points=[cx - wd, cy + r * .2, cx + wd, cy + r * .2, cx, cy - r])
    Color(.85, .97, 1, a * .8)
    Triangle(points=[cx - wd * .5, cy + r, cx - wd * .1, cy + r * .2, cx - wd * .8, cy + r * .2])
