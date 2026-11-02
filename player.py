"""Procedural character art (4 unique runners). Drawn with canvas shapes, so every
character the UI shows really exists. Used for menu, selection and gameplay."""
import math

from kivy.graphics import (Color, Ellipse, Line, PopMatrix, PushMatrix, Rectangle,
                           RoundedRectangle, Rotate, Triangle)

PAL = {
    'robo': dict(skin=(.96, .76, .62), hair=(.07, .06, .09), top=(.09, .09, .12), accent=(.92, .10, .15),
                 pants=(.10, .10, .14), shoe=(.92, .10, .15), sole=(.96, .96, .96), glow=(.2, .9, 1.0)),
    'female': dict(skin=(.97, .78, .66), hair=(.50, .22, .12), top=(.55, .20, .78), accent=(1.0, .42, .72),
                   pants=(.13, .13, .22), shoe=(.96, .96, 1.0), sole=(1.0, .42, .72), glow=(1.0, .5, .8)),
    'shadow': dict(skin=(.05, .04, .08), hair=(.14, .09, .24), top=(.13, .08, .22), accent=(.72, .30, 1.0),
                   pants=(.07, .06, .12), shoe=(.16, .10, .26), sole=(.72, .30, 1.0), glow=(.85, .45, 1.0)),
    'panda': dict(skin=(.97, .97, .97), hair=(.05, .05, .05), top=(.96, .96, .96), accent=(.12, .12, .12),
                  pants=(.08, .08, .08), shoe=(.10, .10, .10), sole=(.92, .92, .92), glow=(.4, 1.0, .6)),
}


def draw_runner(kind, cx, by, h, phase=0.0, pose='run', front=False, alpha=1.0, shadow=True):
    """Draw one runner. (cx, by) = bottom centre, h = full height in px.
    pose: run | jump | slide | idle.  front=True shows the face, False the back."""
    p = PAL.get(kind, PAL['robo'])
    u = h
    al = alpha

    def col(c, a=1.0):
        Color(c[0], c[1], c[2], a * al)

    if shadow and pose != 'slide':
        Color(0, 0, 0, 0.35 * al)
        Ellipse(pos=(cx - .22 * u, by - .025 * u), size=(.44 * u, .07 * u))

    rot = pose == 'slide'
    if rot:
        PushMatrix()
        Rotate(angle=62, origin=(cx, by + .12 * u))
        by += .02 * u

    swing = math.sin(phase) if pose == 'run' else 0.0

    # legs
    for side in (-1, 1):
        sv = swing * side
        if pose == 'jump':
            lift, dx = .10 * u, side * .06 * u
        else:
            lift, dx = max(0.0, sv) * .10 * u, sv * .05 * u
        lx = cx + side * .075 * u + dx
        col(p['pants'])
        RoundedRectangle(pos=(lx - .055 * u, by + .09 * u + lift), size=(.11 * u, .40 * u), radius=[.04 * u])
        col(p['shoe'])
        RoundedRectangle(pos=(lx - .075 * u, by + lift), size=(.15 * u, .10 * u), radius=[.04 * u])
        col(p['sole'])
        Rectangle(pos=(lx - .075 * u, by + lift), size=(.15 * u, .022 * u))

    # arms (behind torso)
    for side in (-1, 1):
        sv = -swing * side
        ay = by + .40 * u + sv * .03 * u
        if pose == 'jump':
            ay = by + .50 * u
        col(p['top'])
        RoundedRectangle(pos=(cx + side * .18 * u - .042 * u, ay), size=(.084 * u, .27 * u), radius=[.04 * u])
        col(p['accent'] if kind != 'panda' else p['hair'])
        Ellipse(pos=(cx + side * .18 * u - .05 * u, ay - .035 * u), size=(.10 * u, .09 * u))

    # torso / hoodie
    col(p['top'])
    RoundedRectangle(pos=(cx - .155 * u, by + .44 * u), size=(.31 * u, .31 * u), radius=[.07 * u])
    col(p['accent'])
    Rectangle(pos=(cx - .155 * u, by + .44 * u), size=(.31 * u, .035 * u))
    if kind == 'panda':
        col(p['hair'])
        Rectangle(pos=(cx - .155 * u, by + .53 * u), size=(.31 * u, .045 * u))
    if kind == 'robo' and not front:
        col(p['glow'])
        s = .10 * u
        Line(points=[cx - .04 * u, by + .54 * u, cx - .04 * u, by + .54 * u + s, cx + .02 * u, by + .54 * u + s,
                     cx + .04 * u, by + .54 * u + s * .7, cx + .02 * u, by + .54 * u + s * .5,
                     cx - .04 * u, by + .54 * u + s * .5, cx + .05 * u, by + .54 * u],
             width=max(1.0, .012 * u))
    if front:
        col(p['accent'], 0.9)
        Rectangle(pos=(cx - .012 * u, by + .46 * u), size=(.024 * u, .22 * u))
    # hood / collar
    col(p['accent'] if kind in ('robo', 'female') else p['top'])
    Ellipse(pos=(cx - .13 * u, by + .70 * u), size=(.26 * u, .10 * u))

    # head
    hx, hy, hw, hh = cx - .115 * u, by + .74 * u, .23 * u, .25 * u
    if kind == 'panda':
        col(p['hair'])
        Ellipse(pos=(hx - .02 * u, hy + .17 * u), size=(.09 * u, .09 * u))
        Ellipse(pos=(hx + hw - .07 * u, hy + .17 * u), size=(.09 * u, .09 * u))
        col(p['skin'])
        Ellipse(pos=(hx - .015 * u, hy), size=(hw + .03 * u, hh))
        if front:
            col(p['hair'])
            Ellipse(pos=(hx + .02 * u, hy + .08 * u), size=(.07 * u, .09 * u))
            Ellipse(pos=(hx + hw - .09 * u, hy + .08 * u), size=(.07 * u, .09 * u))
            Ellipse(pos=(cx - .02 * u, hy + .06 * u), size=(.04 * u, .03 * u))
            col((1, 1, 1))
            Ellipse(pos=(hx + .045 * u, hy + .115 * u), size=(.02 * u, .02 * u))
            Ellipse(pos=(hx + hw - .065 * u, hy + .115 * u), size=(.02 * u, .02 * u))
    elif kind == 'shadow':
        col(p['hair'])
        Ellipse(pos=(hx - .03 * u, hy - .02 * u), size=(hw + .06 * u, hh + .06 * u))
        Triangle(points=[hx - .03 * u, hy + .12 * u, hx + hw + .03 * u, hy + .12 * u, cx, hy + hh + .13 * u])
        if front:
            col((0, 0, 0))
            Ellipse(pos=(hx + .01 * u, hy + .02 * u), size=(hw - .02 * u, hh - .05 * u))
            col(p['glow'])
            Ellipse(pos=(hx + .035 * u, hy + .11 * u), size=(.045 * u, .03 * u))
            Ellipse(pos=(hx + hw - .08 * u, hy + .11 * u), size=(.045 * u, .03 * u))
    else:
        col(p['skin'])
        Ellipse(pos=(hx, hy), size=(hw, hh))
        col(p['hair'])
        if kind == 'female':
            Ellipse(pos=(hx + hw - .03 * u, hy - .04 * u), size=(.10 * u, .24 * u))      # ponytail
            Ellipse(pos=(hx - .01 * u, hy + .08 * u), size=(hw + .02 * u, hh * .72))
        else:
            Ellipse(pos=(hx - .005 * u, hy + .07 * u if front else hy), size=(hw + .01 * u, hh * (.62 if front else 1.0)))
            for i in range(3):
                bx = hx + i * hw / 3.0
                Triangle(points=[bx, hy + hh * .82, bx + hw / 3.0, hy + hh * .82, bx + hw / 6.0 + (i - 1) * .02 * u, hy + hh + .10 * u])
        if front:
            col((.1, .1, .15))
            Ellipse(pos=(hx + .045 * u, hy + .075 * u), size=(.04 * u, .05 * u))
            Ellipse(pos=(hx + hw - .085 * u, hy + .075 * u), size=(.04 * u, .05 * u))
            col((1, 1, 1))
            Ellipse(pos=(hx + .055 * u, hy + .105 * u), size=(.014 * u, .014 * u))
            Ellipse(pos=(hx + hw - .075 * u, hy + .105 * u), size=(.014 * u, .014 * u))

    if rot:
        PopMatrix()
