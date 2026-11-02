"""Reusable neon / glass UI built from Kivy canvas instructions (no image files)."""
import math
import random

from kivy.clock import Clock
from kivy.graphics import (Color, Ellipse, Line, Quad, Rectangle, RoundedRectangle, Triangle)
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget

import assets
import player

GOLD = (1.0, 0.80, 0.12, 1)
CYAN = (0.2, 0.75, 1.0, 1)
WHITE = (1, 1, 1, 1)

_GRAD = {}


def gradient(top, bottom):
    """Cached vertical gradient texture (top/bottom are RGBA 0..1 tuples)."""
    key = (tuple(top), tuple(bottom))
    t = _GRAD.get(key)
    if t is None:
        n = 48
        buf = bytearray()
        for i in range(n):
            f = i / (n - 1.0)
            for k in range(4):
                buf.append(int(255 * (bottom[k] * (1 - f) + top[k] * f)))
        t = Texture.create(size=(1, n), colorfmt='rgba')
        t.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
        t.mag_filter = 'linear'
        t.min_filter = 'linear'
        _GRAD[key] = t
    return t


def _poly(points):
    """Fill a star-shaped polygon with a triangle fan around its centroid."""
    n = len(points) // 2
    cx = sum(points[0::2]) / n
    cy = sum(points[1::2]) / n
    for i in range(n):
        j = (i + 1) % n
        Triangle(points=[cx, cy, points[2 * i], points[2 * i + 1], points[2 * j], points[2 * j + 1]])


def _arc(cx, cy, r, a0, a1, n=16):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts += [cx + math.cos(a) * r, cy + math.sin(a) * r]
    return pts


def draw_icon(name, cx, cy, s, c=WHITE):
    """Vector icon centred on (cx, cy), about s pixels tall. Some icons keep their own
    colours (coin, diamond, crown, trophy, star, heart, bolt, magnet)."""
    a = c[3]
    Color(*c)
    if name == 'play':
        Triangle(points=[cx - .35 * s, cy - .45 * s, cx - .35 * s, cy + .45 * s, cx + .45 * s, cy])
    elif name == 'pause':
        Rectangle(pos=(cx - .30 * s, cy - .40 * s), size=(.22 * s, .80 * s))
        Rectangle(pos=(cx + .08 * s, cy - .40 * s), size=(.22 * s, .80 * s))
    elif name == 'gear':
        for k in range(8):
            ang = k * math.pi / 4
            Line(points=[cx + math.cos(ang) * .36 * s, cy + math.sin(ang) * .36 * s,
                         cx + math.cos(ang) * .52 * s, cy + math.sin(ang) * .52 * s],
                 width=max(1.0, .13 * s), cap='square')
        Line(circle=(cx, cy, .30 * s), width=max(1.0, .11 * s))
    elif name == 'user':
        Ellipse(pos=(cx - .17 * s, cy + .02 * s), size=(.34 * s, .36 * s))
        Ellipse(pos=(cx - .34 * s, cy - .48 * s), size=(.68 * s, .56 * s))
    elif name == 'trophy':
        Color(1.0, .80, .15, a)
        Quad(points=[cx - .34 * s, cy + .42 * s, cx + .34 * s, cy + .42 * s, cx + .20 * s, cy - .08 * s, cx - .20 * s, cy - .08 * s])
        Line(circle=(cx - .36 * s, cy + .24 * s, .13 * s), width=max(1.0, .05 * s))
        Line(circle=(cx + .36 * s, cy + .24 * s, .13 * s), width=max(1.0, .05 * s))
        Rectangle(pos=(cx - .06 * s, cy - .30 * s), size=(.12 * s, .24 * s))
        Color(.85, .55, .05, a)
        RoundedRectangle(pos=(cx - .25 * s, cy - .48 * s), size=(.50 * s, .17 * s), radius=[.04 * s])
        Color(1, .95, .6, .55 * a)
        Quad(points=[cx - .24 * s, cy + .36 * s, cx - .14 * s, cy + .36 * s, cx - .08 * s, cy - .02 * s, cx - .14 * s, cy - .02 * s])
        Color(1, .95, .6, a)
        Ellipse(pos=(cx - .34 * s, cy + .37 * s), size=(.68 * s, .10 * s))
    elif name == 'exit':
        Line(points=[cx + .05 * s, cy + .42 * s, cx - .32 * s, cy + .42 * s, cx - .32 * s, cy - .42 * s, cx + .05 * s, cy - .42 * s],
             width=max(1.0, .09 * s))
        Line(points=[cx - .08 * s, cy, cx + .38 * s, cy], width=max(1.0, .09 * s))
        Triangle(points=[cx + .30 * s, cy + .16 * s, cx + .30 * s, cy - .16 * s, cx + .48 * s, cy])
    elif name == 'home':
        Triangle(points=[cx - .48 * s, cy + .05 * s, cx + .48 * s, cy + .05 * s, cx, cy + .48 * s])
        Rectangle(pos=(cx - .34 * s, cy - .42 * s), size=(.68 * s, .50 * s))
        Color(0, 0, 0, .35 * a)
        Rectangle(pos=(cx - .09 * s, cy - .42 * s), size=(.18 * s, .32 * s))
    elif name == 'restart':
        Line(points=_arc(cx, cy, .33 * s, 60, 330, 22), width=max(1.0, .11 * s), cap='round')
        ang = math.radians(330)
        px, py = cx + math.cos(ang) * .33 * s, cy + math.sin(ang) * .33 * s
        tx, ty = -math.sin(ang), math.cos(ang)
        nx, ny = math.cos(ang), math.sin(ang)
        Triangle(points=[px + tx * .26 * s, py + ty * .26 * s, px + nx * .20 * s, py + ny * .20 * s, px - nx * .20 * s, py - ny * .20 * s])
    elif name == 'check':
        Line(points=[cx - .36 * s, cy, cx - .10 * s, cy - .28 * s, cx + .38 * s, cy + .32 * s],
             width=max(1.0, .14 * s), cap='round', joint='round')
    elif name in ('back', 'left'):
        Line(points=[cx + .14 * s, cy + .38 * s, cx - .22 * s, cy, cx + .14 * s, cy - .38 * s],
             width=max(1.0, .14 * s), cap='round', joint='round')
    elif name == 'right':
        Line(points=[cx - .14 * s, cy + .38 * s, cx + .22 * s, cy, cx - .14 * s, cy - .38 * s],
             width=max(1.0, .14 * s), cap='round', joint='round')
    elif name == 'next':
        for dx in (-.18, .12):
            Line(points=[cx + (dx - .12) * s, cy + .34 * s, cx + (dx + .16) * s, cy, cx + (dx - .12) * s, cy - .34 * s],
                 width=max(1.0, .13 * s), cap='round', joint='round')
    elif name == 'coin':
        Color(1.0, .78, .10, a)
        Ellipse(pos=(cx - .42 * s, cy - .42 * s), size=(.84 * s, .84 * s))
        Color(.85, .50, .04, a)
        Line(circle=(cx, cy, .30 * s), width=max(1.0, .07 * s))
        Color(1, 1, .8, .7 * a)
        Ellipse(pos=(cx - .22 * s, cy + .05 * s), size=(.14 * s, .20 * s))
    elif name == 'diamond':
        Color(.15, .65, 1.0, a)
        Quad(points=[cx - .42 * s, cy + .16 * s, cx - .22 * s, cy + .42 * s, cx + .22 * s, cy + .42 * s, cx + .42 * s, cy + .16 * s])
        Color(.05, .45, .9, a)
        Triangle(points=[cx - .42 * s, cy + .16 * s, cx + .42 * s, cy + .16 * s, cx, cy - .46 * s])
        Color(.8, .95, 1, .8 * a)
        Triangle(points=[cx - .22 * s, cy + .42 * s, cx - .08 * s, cy + .16 * s, cx - .34 * s, cy + .16 * s])
    elif name == 'crown':
        Color(1.0, .80, .12, a)
        Rectangle(pos=(cx - .46 * s, cy - .32 * s), size=(.92 * s, .24 * s))
        Triangle(points=[cx - .46 * s, cy - .08 * s, cx - .46 * s, cy + .40 * s, cx - .16 * s, cy - .08 * s])
        Triangle(points=[cx - .24 * s, cy - .08 * s, cx, cy + .50 * s, cx + .24 * s, cy - .08 * s])
        Triangle(points=[cx + .16 * s, cy - .08 * s, cx + .46 * s, cy + .40 * s, cx + .46 * s, cy - .08 * s])
        Color(.9, .15, .25, a)
        Ellipse(pos=(cx - .09 * s, cy - .27 * s), size=(.18 * s, .15 * s))
    elif name == 'star':
        pts = []
        for i in range(10):
            ang = math.radians(90 + i * 36)
            r = .48 * s if i % 2 == 0 else .20 * s
            pts += [cx + math.cos(ang) * r, cy + math.sin(ang) * r - .02 * s]
        _poly(pts)
    elif name == 'heart':
        Ellipse(pos=(cx - .44 * s, cy - .02 * s), size=(.46 * s, .46 * s))
        Ellipse(pos=(cx - .02 * s, cy - .02 * s), size=(.46 * s, .46 * s))
        Triangle(points=[cx - .43 * s, cy + .12 * s, cx + .45 * s, cy + .12 * s, cx, cy - .44 * s])
    elif name == 'bolt':
        Color(1.0, .82, .1, a)
        Triangle(points=[cx + .10 * s, cy + .5 * s, cx - .30 * s, cy - .06 * s, cx + .04 * s, cy - .06 * s])
        Triangle(points=[cx - .10 * s, cy - .5 * s, cx + .30 * s, cy + .06 * s, cx - .04 * s, cy + .06 * s])
    elif name == 'magnet':
        Color(.95, .2, .6, a)
        pts = [cx - .30 * s, cy + .40 * s, cx - .30 * s, cy] + _arc(cx, cy, .30 * s, 180, 360, 14) + [cx + .30 * s, cy + .40 * s]
        Line(points=pts, width=max(1.0, .16 * s), cap='square', joint='round')
        Color(1, 1, 1, a)
        Rectangle(pos=(cx - .38 * s, cy + .34 * s), size=(.16 * s, .12 * s))
        Rectangle(pos=(cx + .22 * s, cy + .34 * s), size=(.16 * s, .12 * s))
    elif name == 'music':
        Ellipse(pos=(cx - .34 * s, cy - .40 * s), size=(.34 * s, .26 * s))
        Line(points=[cx - .02 * s, cy - .27 * s, cx - .02 * s, cy + .40 * s], width=max(1.0, .08 * s))
        Line(points=[cx - .02 * s, cy + .40 * s, cx + .30 * s, cy + .22 * s], width=max(1.0, .10 * s))
    elif name == 'speaker':
        Rectangle(pos=(cx - .42 * s, cy - .14 * s), size=(.20 * s, .28 * s))
        Triangle(points=[cx - .22 * s, cy + .14 * s, cx - .22 * s, cy - .14 * s, cx + .08 * s, cy - .42 * s])
        Triangle(points=[cx - .22 * s, cy + .14 * s, cx + .08 * s, cy + .42 * s, cx + .08 * s, cy - .42 * s])
        Line(points=_arc(cx + .08 * s, cy, .22 * s, -45, 45, 8), width=max(1.0, .07 * s))
        Line(points=_arc(cx + .08 * s, cy, .38 * s, -45, 45, 8), width=max(1.0, .07 * s))
    elif name == 'monitor':
        Line(rounded_rectangle=(cx - .46 * s, cy - .20 * s, .92 * s, .62 * s, .05 * s), width=max(1.0, .07 * s))
        Line(points=[cx, cy - .20 * s, cx, cy - .36 * s], width=max(1.0, .07 * s))
        Line(points=[cx - .22 * s, cy - .38 * s, cx + .22 * s, cy - .38 * s], width=max(1.0, .07 * s))
    elif name == 'gamepad':
        RoundedRectangle(pos=(cx - .50 * s, cy - .26 * s), size=(1.0 * s, .56 * s), radius=[.22 * s])
        Color(0, 0, 0, .65 * a)
        Rectangle(pos=(cx - .34 * s, cy - .04 * s), size=(.24 * s, .07 * s))
        Rectangle(pos=(cx - .255 * s, cy - .125 * s), size=(.07 * s, .24 * s))
        Ellipse(pos=(cx + .12 * s, cy - .10 * s), size=(.11 * s, .11 * s))
        Ellipse(pos=(cx + .27 * s, cy + .02 * s), size=(.11 * s, .11 * s))
    elif name == 'globe':
        Line(circle=(cx, cy, .42 * s), width=max(1.0, .07 * s))
        Line(ellipse=(cx - .17 * s, cy - .42 * s, .34 * s, .84 * s), width=max(1.0, .06 * s))
        Line(points=[cx - .42 * s, cy, cx + .42 * s, cy], width=max(1.0, .06 * s))
    elif name == 'lock':
        Line(points=_arc(cx, cy + .08 * s, .20 * s, 0, 180, 10), width=max(1.0, .08 * s))
        RoundedRectangle(pos=(cx - .30 * s, cy - .40 * s), size=(.60 * s, .46 * s), radius=[.06 * s])
    elif name == 'phone':
        Line(rounded_rectangle=(cx - .22 * s, cy - .44 * s, .44 * s, .88 * s, .06 * s), width=max(1.0, .07 * s))
        Ellipse(pos=(cx - .04 * s, cy - .38 * s), size=(.08 * s, .08 * s))


class IconWidget(Widget):
    name = StringProperty('')
    tint = ListProperty([1, 1, 1, 1])
    scale = NumericProperty(0.9)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, name=self._draw, tint=self._draw)
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            draw_icon(self.name, self.center_x, self.center_y, min(self.width, self.height) * self.scale, tuple(self.tint))


class FLabel(Label):
    """Label whose font size follows its own height (responsive on any screen)."""
    frac = NumericProperty(0.5)

    def __init__(self, **kw):
        kw.setdefault('halign', 'center')
        kw.setdefault('valign', 'middle')
        super().__init__(**kw)
        self.bind(size=self._fit, frac=self._fit)
        self._fit()

    def _fit(self, *a):
        self.font_size = max(6.0, self.height * self.frac)
        self.text_size = (self.width, self.height)


STYLES = {
    # top, bottom, border, text
    'gold': ((1.0, 0.86, 0.22, 1), (1.0, 0.52, 0.04, 1), (1.0, 0.93, 0.5, 1), (0.16, 0.08, 0.0, 1)),
    'blue': ((0.10, 0.27, 0.62, 1), (0.03, 0.08, 0.28, 1), (0.25, 0.75, 1.0, 1), (1, 1, 1, 1)),
    'green': ((0.25, 0.90, 0.28, 1), (0.02, 0.48, 0.10, 1), (0.60, 1.0, 0.55, 1), (1, 1, 1, 1)),
    'purple': ((0.68, 0.28, 1.0, 1), (0.34, 0.05, 0.72, 1), (0.88, 0.60, 1.0, 1), (1, 1, 1, 1)),
    'red': ((0.95, 0.25, 0.25, 1), (0.55, 0.05, 0.10, 1), (1.0, 0.6, 0.6, 1), (1, 1, 1, 1)),
}


class NeonButton(ButtonBehavior, Widget):
    text = StringProperty('')
    icon = StringProperty('')
    style = StringProperty('blue')
    fs = NumericProperty(0.40)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._lbl = Label(bold=True, italic=True, halign='center', valign='middle')
        self.add_widget(self._lbl)
        self.bind(pos=self._draw, size=self._draw, state=self._draw, text=self._draw,
                  style=self._draw, icon=self._draw, disabled=self._draw, fs=self._draw)
        self.bind(on_release=lambda *a: assets.play('click'))
        self._draw()

    def _draw(self, *a):
        top, bot, bd, tc = STYLES.get(self.style, STYLES['blue'])
        k = 0.45 if self.disabled else 1.0
        x, y, w, h = self.x, self.y, self.width, self.height
        if self.state == 'down':
            x += w * 0.015
            y += h * 0.03
            w *= 0.97
            h *= 0.94
        r = h * 0.28
        self.canvas.before.clear()
        with self.canvas.before:
            Color(bd[0], bd[1], bd[2], 0.20 * k)
            RoundedRectangle(pos=(x - h * 0.08, y - h * 0.08), size=(w + h * 0.16, h * 1.16), radius=[r * 1.3])
            Color(1, 1, 1, k)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r], texture=gradient(top, bot))
            Color(bd[0], bd[1], bd[2], k)
            Line(rounded_rectangle=(x, y, w, h, r), width=max(1.2, h * 0.035))
            Color(1, 1, 1, 0.20 * k)
            RoundedRectangle(pos=(x + w * 0.03, y + h * 0.54), size=(w * 0.94, h * 0.40), radius=[r * 0.8])
            if self.icon:
                draw_icon(self.icon, x + h * 0.55, y + h * 0.5, h * 0.52, (tc[0], tc[1], tc[2], k))
        off = h * 1.0 if self.icon else 0
        lb = self._lbl
        lb.text = self.text
        lb.font_size = max(6.0, h * self.fs)
        lb.color = (tc[0], tc[1], tc[2], k)
        lb.pos = (x + off, y)
        lb.size = (w - off, h)
        lb.text_size = (w - off, h)


class GlassPanel(Widget):
    border = ListProperty([0.2, 0.75, 1.0, 1])
    fill = ListProperty([0.03, 0.07, 0.20, 0.90])
    radius_frac = NumericProperty(0.05)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, border=self._draw, fill=self._draw)
        self._draw()

    def _draw(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        r = min(w, self.height) * self.radius_frac
        f, b = self.fill, self.border
        self.canvas.clear()
        with self.canvas:
            Color(b[0], b[1], b[2], 0.16)
            RoundedRectangle(pos=(x - r * .35, y - r * .35), size=(w + r * .7, h + r * .7), radius=[r * 1.2])
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r],
                             texture=gradient((f[0] * 1.5, f[1] * 1.5, f[2] * 1.4, f[3]), (f[0] * .6, f[1] * .6, f[2] * .8, f[3])))
            Color(b[0], b[1], b[2], 1)
            Line(rounded_rectangle=(x, y, w, h, r), width=max(1.2, min(w, h) * 0.006))
            Color(b[0], b[1], b[2], 0.30)
            Line(rounded_rectangle=(x + r * .35, y + r * .35, w - r * .7, h - r * .7, r * .7), width=1)


class NeonToggle(ButtonBehavior, Widget):
    value = BooleanProperty(True)
    __events__ = ('on_toggle',)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, value=self._draw)
        self._draw()

    def on_release(self):
        assets.play('click')
        self.value = not self.value
        self.dispatch('on_toggle', self.value)

    def on_toggle(self, v):
        pass

    def _draw(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        self.canvas.clear()
        with self.canvas:
            if self.value:
                Color(0.10, 0.60, 1.0, 1)
            else:
                Color(0.18, 0.20, 0.32, 1)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[h / 2])
            Color(0.5, 0.9, 1.0, 1 if self.value else 0.4)
            Line(rounded_rectangle=(x, y, w, h, h / 2), width=1.3)
            Color(1, 1, 1, 1)
            kx = x + w - h * 0.92 if self.value else x + h * 0.08
            Ellipse(pos=(kx, y + h * 0.08), size=(h * 0.84, h * 0.84))


class ArrowButton(ButtonBehavior, Widget):
    direction = NumericProperty(1)   # -1 left, +1 right

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, state=self._draw)
        self.bind(on_release=lambda *a: assets.play('click'))
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            c = (1, 1, 1, 0.6) if self.state == 'down' else (1, 1, 1, 1)
            draw_icon('left' if self.direction < 0 else 'right', self.center_x, self.center_y,
                      min(self.width, self.height) * 0.9, c)


class TiltBar(Widget):
    """Shows the live calibrated tilt so the player can verify the sensor works."""
    value = NumericProperty(0.0)
    limit = NumericProperty(5.0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, value=self._draw)

    def _draw(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        self.canvas.clear()
        with self.canvas:
            Color(0.1, 0.15, 0.3, 1)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[h / 2])
            Color(0.2, 0.75, 1, 0.8)
            Line(rounded_rectangle=(x, y, w, h, h / 2), width=1.2)
            Color(1, 1, 1, 0.5)
            Rectangle(pos=(x + w / 2 - 1, y + h * 0.15), size=(2, h * 0.7))
            v = max(-1.0, min(1.0, self.value / self.limit))
            Color(1.0, 0.8, 0.15, 1)
            Ellipse(pos=(x + w / 2 + v * (w / 2 - h / 2) - h * 0.4, y + h * 0.1), size=(h * 0.8, h * 0.8))


class CityBackground(Widget):
    mode = StringProperty('home')
    quality = StringProperty('High')

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self.draw, size=self.draw, mode=self.draw, quality=self.draw)

    def draw(self, *a):
        w, h = self.size
        ox, oy = self.pos
        self.canvas.clear()
        if w < 2 or h < 2:
            return
        rnd = random.Random(21)
        home = self.mode == 'home'
        top, bot = (((0.02, 0.03, 0.14, 1), (0.36, 0.12, 0.52, 1)) if home
                    else ((0.01, 0.02, 0.10, 1), (0.03, 0.12, 0.40, 1)))
        wins = {'Low': 0.0, 'Medium': 0.45, 'High': 1.0}.get(self.quality, 1.0)
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=gradient(top, bot), pos=self.pos, size=self.size)
            for _ in range(int(40 * (wins + .3))):
                Color(1, 1, 1, rnd.uniform(.2, .8))
                r = rnd.uniform(1, 2.4)
                Ellipse(pos=(ox + rnd.random() * w, oy + h * (0.55 + rnd.random() * 0.45)), size=(r, r))
            if home:
                mx, my, mr = ox + w * 0.50, oy + h * 0.76, w * 0.085
                for i, al in enumerate((0.05, 0.08, 0.12)):
                    Color(0.7, 0.8, 1, al)
                    rr = mr * (2.4 - i * .5)
                    Ellipse(pos=(mx - rr, my - rr), size=(rr * 2, rr * 2))
                Color(0.90, 0.93, 1, 1)
                Ellipse(pos=(mx - mr, my - mr), size=(mr * 2, mr * 2))
                Color(0.65, 0.70, 0.9, 0.5)
                for dx, dy, rr in ((-.3, .2, .22), (.25, -.15, .18), (.05, .35, .12)):
                    Ellipse(pos=(mx + dx * mr - rr * mr, my + dy * mr - rr * mr), size=(rr * mr * 2, rr * mr * 2))
            layers = [(0.30, (0.11, 0.10, 0.32, 1), 0.20, 0.0), (0.25, (0.07, 0.07, 0.25, 1), 0.28, 0.5),
                      (0.20, (0.035, 0.04, 0.15, 1), 0.36, 1.0)]
            neon = [(1.0, 0.2, 0.7), (0.2, 0.9, 1.0), (1.0, 0.85, 0.2), (0.7, 0.3, 1.0)]
            for base, col, hmax, lit in layers:
                x = -w * 0.02
                while x < w:
                    bw = w * rnd.uniform(0.07, 0.15)
                    bh = h * rnd.uniform(hmax * 0.4, hmax)
                    by = oy + h * base
                    Color(*col)
                    Rectangle(pos=(ox + x, by), size=(bw, bh))
                    Color(0.3, 0.5, 1, 0.35)
                    Rectangle(pos=(ox + x, by + bh - 2), size=(bw, 2))
                    if lit and wins > 0:
                        cols = max(2, int(bw / (w * 0.022)))
                        rows = max(2, int(bh / (h * 0.018)))
                        cw, rh = bw / (cols + 1), bh / (rows + 1)
                        for ci in range(cols):
                            for ri in range(rows):
                                if rnd.random() < 0.38 * wins * lit:
                                    n = neon[rnd.randrange(4)] if rnd.random() < .35 else (1.0, .85, .5)
                                    Color(n[0], n[1], n[2], 0.85)
                                    Rectangle(pos=(ox + x + (ci + .6) * cw, by + (ri + .6) * rh), size=(cw * .45, rh * .45))
                        if home and rnd.random() < 0.22:
                            n = neon[rnd.randrange(4)]
                            Color(n[0], n[1], n[2], 0.95)
                            Line(rounded_rectangle=(ox + x + bw * .2, by + bh * .55, bw * .6, bh * .22, 4), width=2)
                            Color(n[0], n[1], n[2], 0.25)
                            RoundedRectangle(pos=(ox + x + bw * .2, by + bh * .55), size=(bw * .6, bh * .22), radius=[4])
                    x += bw + w * rnd.uniform(0.0, 0.015)
            if home:
                fy = oy + h * 0.30
                Color(1, 1, 1, 1)
                Rectangle(texture=gradient((0.22, 0.24, 0.48, 1), (0.04, 0.05, 0.14, 1)), pos=(ox, oy), size=(w, fy - oy))
                Color(0.3, 0.5, 1, 0.20)
                for i in range(-7, 8):
                    Line(points=[ox + w * .5 + i * w * .09, fy, ox + w * .5 + i * w * .24, oy], width=1)
                for j in range(1, 5):
                    yy = fy - (fy - oy) * (j / 5.0) ** 1.6
                    Line(points=[ox, yy, ox + w, yy], width=1)
                Color(0.2, 0.85, 1, 0.9)
                Line(points=[ox, fy, ox + w, fy], width=max(2, h * 0.003))
                Color(0.2, 0.85, 1, 0.18)
                Rectangle(pos=(ox, fy - h * 0.012), size=(w, h * 0.024))
                for i in range(0, 9):
                    px = ox + w * (i / 8.0)
                    Color(0.1, 0.12, 0.3, 1)
                    Rectangle(pos=(px - 3, fy), size=(6, h * 0.035))
                    Color(1.0, 0.3, 0.75, 0.9)
                    Ellipse(pos=(px - 4, fy + h * 0.033), size=(8, 8))


class RunnerFigure(Widget):
    kind = StringProperty('robo')
    front = BooleanProperty(False)
    animate = BooleanProperty(False)
    dim = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._t = 0.0
        self._ev = None
        self.bind(pos=self._draw, size=self._draw, kind=self._draw, front=self._draw, dim=self._draw)
        self._draw()

    def on_parent(self, widget, parent):
        if self._ev:
            self._ev.cancel()
            self._ev = None
        if parent is not None and self.animate:
            self._ev = Clock.schedule_interval(self._tick, 1 / 20.0)

    def _tick(self, dt):
        self._t += dt
        self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            bob = 1.0 + 0.010 * math.sin(self._t * 2.4)
            player.draw_runner(self.kind, self.center_x, self.y, self.height * bob, phase=0.0,
                               pose='idle', front=self.front, alpha=0.45 if self.dim else 1.0)
