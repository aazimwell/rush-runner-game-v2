"""Gameplay: pseudo-3D perspective renderer (2D canvas scaling + depth ordering),
HUD, pause overlay and the result screen.

Honest note: this is NOT a 3D engine. Depth is faked with a perspective projection
s = 1/(1+0.075 z) that scales every sprite and positions it between the horizon and the
player line, drawn far-to-near.
"""
import math
import random

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Quad, Rectangle
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

import characters
import coins
import obstacles
import player
import settings as cfg
from controls import SwipeDetector
from game_logic import World
from menu import BaseScreen, GOLD, ICE, _ow
from ui_components import FLabel, GlassPanel, IconWidget, NeonButton, CityBackground, draw_icon, gradient

FARZ = 84.0
HAZE = (0.33, 0.14, 0.48)
NEON = [(0.2, 0.9, 1.0), (1.0, 0.3, 0.75), (1.0, 0.85, 0.25), (0.7, 0.4, 1.0)]


def S(z):
    return 1.0 / (1.0 + max(z, -4.0) * 0.075)


def fogc(col, fog):
    return (col[0] * (1 - fog) + HAZE[0] * fog, col[1] * (1 - fog) + HAZE[1] * fog, col[2] * (1 - fog) + HAZE[2] * fog)


class GameWidget(Widget):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.world = None
        self.dets = {}
        self.enabled = True
        self.on_gesture = None
        rnd = random.Random(5)
        self.sky = []
        x = -0.1
        while x < 1.1:
            wf = rnd.uniform(0.05, 0.11)
            self.sky.append((x, wf, rnd.uniform(0.04, 0.17), rnd.randrange(4)))
            x += wf * rnd.uniform(0.8, 1.1)

    def new_world(self, level):
        self.world = World(characters.get(self.app.save['selected']), level)
        self.dets = {}

    # ---- touch / swipe ---------------------------------------------------
    def on_touch_down(self, touch):
        if self.world is None or not self.enabled or not self.collide_point(*touch.pos):
            return False
        if self.app.save['control'] == 'tilt':
            return False
        touch.grab(self)
        d = SwipeDetector(cfg.SWIPE_FRAC.get(self.app.save['sensitivity'], 0.07))
        d.start(touch.x, touch.y)
        self.dets[touch.uid] = d
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            d = self.dets.get(touch.uid)
            if d and self.enabled:
                g = d.move(touch.x, touch.y, self.width)
                if g and self.on_gesture:
                    self.on_gesture(g)
            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.dets.pop(touch.uid, None)
            return True
        return False

    # ---- rendering -------------------------------------------------------
    def draw(self):
        wd = self.world
        if wd is None or self.width < 2:
            return
        q = self.app.save['quality']
        ox, oy = self.pos
        w, h = self.size
        cx = ox + w / 2.0
        hy = oy + h * 0.60
        py = oy + h * 0.17
        lw = w * 0.30
        dist = wd.dist

        def Y(s):
            return hy - (hy - py) * s

        def X(l, s):
            return cx + l * lw * s

        c = self.canvas
        c.clear()
        with c:
            Color(1, 1, 1, 1)
            Rectangle(texture=gradient((0.02, 0.03, 0.14, 1), (0.40, 0.13, 0.52, 1)),
                      pos=(ox, hy - h * 0.005), size=(w, oy + h - hy + h * 0.005))
            Color(0.03, 0.04, 0.12, 1)
            Rectangle(pos=(ox, oy), size=(w, hy - oy))
            mx, my, mr = ox + w * 0.72 - wd.x * w * 0.01, hy + h * 0.20, w * 0.07
            Color(0.7, 0.8, 1, 0.12)
            Ellipse(pos=(mx - mr * 1.9, my - mr * 1.9), size=(mr * 3.8, mr * 3.8))
            Color(0.92, 0.95, 1, 1)
            Ellipse(pos=(mx - mr, my - mr), size=(mr * 2, mr * 2))
            par = -wd.x * w * 0.02
            for xf, wf, hf, n in self.sky:
                Color(0.09, 0.08, 0.28, 1)
                Rectangle(pos=(ox + xf * w + par, hy), size=(wf * w, hf * h))
                if q != 'Low':
                    nc = NEON[n]
                    Color(nc[0], nc[1], nc[2], 0.55)
                    Rectangle(pos=(ox + xf * w + par, hy + hf * h - 2), size=(wf * w, 2))
            Color(HAZE[0], HAZE[1], HAZE[2], 0.30)
            Rectangle(pos=(ox, hy - h * 0.01), size=(w, h * 0.06))

            sN, sF = S(-4.0), S(FARZ)
            base = math.floor(dist / 6.0)
            for k in range(-1, 15):
                seg = base + k
                za = seg * 6.0 - dist
                zb = za + 6.0
                if zb < -4.0:
                    continue
                sa, sb = S(za), S(zb)
                shade = 0.085 if seg % 2 == 0 else 0.11
                Color(shade * 0.9, shade * 0.95, shade * 1.9, 1)
                Quad(points=[X(-1.5, sa), Y(sa), X(1.5, sa), Y(sa), X(1.5, sb), Y(sb), X(-1.5, sb), Y(sb)])
            Color(0.85, 0.92, 1, 0.75)
            for k in range(-1, 12):
                seg = math.floor(dist / 8.0) + k
                za = seg * 8.0 - dist
                zb = za + 3.5
                if zb < -4.0:
                    continue
                sa, sb = S(za), S(zb)
                for l in (-0.5, 0.5):
                    Quad(points=[X(l - .025, sa), Y(sa), X(l + .025, sa), Y(sa), X(l + .025, sb), Y(sb), X(l - .025, sb), Y(sb)])
            for side, colr in ((-1, (0.2, 0.85, 1.0)), (1, (1.0, 0.3, 0.75))):
                pts = [X(side * 1.5, sN), Y(sN), X(side * 1.5, sF), Y(sF)]
                Color(colr[0], colr[1], colr[2], 0.25)
                Line(points=pts, width=max(4.0, w * 0.012))
                Color(colr[0], colr[1], colr[2], 1)
                Line(points=pts, width=max(1.5, w * 0.004))
            for k in range(0, 9):
                z = (math.floor(dist / 10.0) + k) * 10.0 - dist
                if z < -3.0:
                    continue
                s = S(z)
                u = lw * s
                for side, colr in ((-1, (0.2, 0.85, 1.0)), (1, (1.0, 0.3, 0.75))):
                    Color(colr[0], colr[1], colr[2], 0.9)
                    Rectangle(pos=(X(side * 1.58, s) - u * .03, Y(s)), size=(u * .06, u * .28))

            # buildings (far -> near)
            SP = 14.0
            b0 = math.floor(dist / SP)
            for i in range(7, -1, -1):
                b = b0 + i
                z = b * SP - dist
                if z < -6.0:
                    continue
                s = S(z)
                fog = min(1.0, max(0.0, z / FARZ))
                for side in (-1, 1):
                    hs = ((b * 2654435761) + (side + 2) * 40503) & 0xffffffff
                    r1 = (hs % 97) / 97.0
                    r2 = ((hs >> 8) % 89) / 89.0
                    r3 = ((hs >> 16) % 83) / 83.0
                    hgt, wid, lat = 2.4 + r1 * 4.2, 2.6 + r2 * 1.6, 1.95 + r3 * 0.5
                    xi, xo = X(side * lat, s), X(side * (lat + wid), s)
                    yb, ht = Y(s), hgt * lw * s
                    s2 = S(z + SP * 0.85)
                    xi2, yb2, ht2 = X(side * lat, s2), Y(s2), hgt * lw * s2
                    col = (0.07 + 0.10 * r1, 0.07 + 0.08 * r2, 0.22 + 0.18 * r3)
                    cw = fogc((col[0] * .65, col[1] * .65, col[2] * .65), fog)
                    Color(cw[0], cw[1], cw[2], 1)
                    Quad(points=[xi, yb, xi2, yb2, xi2, yb2 + ht2, xi, yb + ht])
                    cf = fogc(col, fog)
                    Color(cf[0], cf[1], cf[2], 1)
                    x0, bw = min(xi, xo), abs(xo - xi)
                    Rectangle(pos=(x0, yb), size=(bw, ht))
                    nc = NEON[(b + (side > 0)) % 4]
                    Color(nc[0], nc[1], nc[2], 0.85 * (1 - fog * .7))
                    Rectangle(pos=(x0, yb + ht - max(1.5, s * 4)), size=(bw, max(1.5, s * 4)))
                    if (q == 'High' and s > 0.15) or (q == 'Medium' and s > 0.35):
                        cols, rows = max(2, int(wid * 1.2)), max(3, int(hgt * 1.6))
                        cw_, rh_ = bw / (cols + 1), ht / (rows + 1)
                        for ci in range(cols):
                            for ri in range(rows):
                                if ((hs >> ((ci + ri * 3) % 24)) & 1) ^ ((ri * 7 + ci * 3 + b) & 1):
                                    Color(1.0, 0.85, 0.5, 0.8 * (1 - fog))
                                    Rectangle(pos=(x0 + (ci + .6) * cw_, yb + (ri + .6) * rh_), size=(cw_ * .5, rh_ * .45))

            # objects + player, far to near
            vis = [o for o in wd.objs if not o['taken'] and -3.0 < o['at'] - dist < FARZ - 2.0]
            vis.sort(key=lambda o: -o['at'])
            done = [False]

            def draw_player():
                done[0] = True
                px = X(wd.x, 1.0)
                by = py + wd.jy * lw
                Color(0, 0, 0, 0.4)
                Ellipse(pos=(px - .28 * lw, py - .04 * lw), size=(.56 * lw, .10 * lw))
                pose = 'slide' if wd.sliding else ('jump' if wd.jy > 0.03 else 'run')
                al = 0.35 if (wd.invuln > 0 and int(wd.t * 14) % 2 == 0) else 1.0
                player.draw_runner(self.app.save['selected'], px, by, 1.6 * lw * (0.9 if pose == 'slide' else 1.0),
                                   wd.phase, pose, False, al, False)

            for o in vis:
                z = o['at'] - dist
                if not done[0] and z < 0.0:
                    draw_player()
                s = S(z)
                u = lw * s
                x, y = X(o['lane'], s), Y(s)
                a = 1.0 if z < 45 else max(0.0, (FARZ - z) / (FARZ - 45.0))
                k = o['kind']
                if k == 'coin':
                    coins.draw_coin(x, y + u * .45, u * .15, wd.t * 6 + o['at'] * .7, a)
                elif k == 'diamond':
                    coins.draw_diamond(x, y + u * .5, u * .2, wd.t * 5 + o['at'], a)
                else:
                    obstacles.draw_obstacle(k, x, y, u, wd.t, a)
            if not done[0]:
                draw_player()
            if wd.invuln > wd.char['invuln'] - 0.18:
                Color(1, 0, 0, 0.22)
                Rectangle(pos=self.pos, size=self.size)


class HeartsWidget(Widget):
    hp = NumericProperty(0)
    max_hp = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._d, size=self._d, hp=self._d, max_hp=self._d)

    def _d(self, *a):
        self.canvas.clear()
        n = int(self.max_hp)
        if n <= 0:
            return
        s = min(self.height, self.width / n)
        x0 = self.right - s * n
        with self.canvas:
            for i in range(n):
                col = (1.0, 0.2, 0.3, 1) if i < self.hp else (0.3, 0.25, 0.38, 0.9)
                draw_icon('heart', x0 + (i + .5) * s, self.center_y, s * 0.85, col)


class Overlay(FloatLayout):
    """Full-screen dimmed layer that swallows every touch."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._d, size=self._d)
        self._d()

    def _d(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.62)
            Rectangle(pos=self.pos, size=self.size)

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        return True


class GameScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, 'game', **kw)
        self.paused = False
        self.level = 1
        self._ev = None
        self._ending = False
        self.overlay = None
        self._last = {}
        self.gw = GameWidget(app, size_hint=(1, 1))
        self.gw.on_gesture = self.apply
        root = FloatLayout()
        root.add_widget(self.gw)
        pb = NeonButton(icon='pause', style='blue', size_hint=(.13, .06), pos_hint={'x': .03, 'top': .985})
        pb.bind(on_release=lambda *a: self.pause())
        root.add_widget(pb)
        root.add_widget(GlassPanel(size_hint=(.50, .07), pos_hint={'x': .20, 'top': .985}, radius_frac=.3))
        root.add_widget(IconWidget(name='trophy', size_hint=(.09, .05), pos_hint={'x': .215, 'top': .975}))
        self.l_score = FLabel(text='0', bold=True, italic=True, frac=.70, halign='left',
                              size_hint=(.26, .05), pos_hint={'x': .31, 'top': .975})
        self.l_mult = FLabel(text='x1', bold=True, italic=True, frac=.62, halign='right', color=GOLD,
                             size_hint=(.12, .05), pos_hint={'x': .56, 'top': .975})
        root.add_widget(self.l_score)
        root.add_widget(self.l_mult)
        root.add_widget(GlassPanel(size_hint=(.26, .045), pos_hint={'x': .20, 'top': .91}, radius_frac=.3))
        root.add_widget(IconWidget(name='coin', size_hint=(.07, .035), pos_hint={'x': .21, 'top': .905}))
        self.l_coins = FLabel(text='0', bold=True, frac=.62, halign='left', size_hint=(.16, .035),
                              pos_hint={'x': .29, 'top': .905})
        root.add_widget(self.l_coins)
        root.add_widget(GlassPanel(size_hint=(.24, .07), pos_hint={'right': .97, 'top': .985}, radius_frac=.3))
        self.l_dist = FLabel(text='0 m', bold=True, frac=.55, size_hint=(.22, .033), pos_hint={'right': .96, 'top': .975})
        self.l_speed = FLabel(text='', frac=.50, color=ICE, size_hint=(.22, .028), pos_hint={'right': .96, 'top': .944})
        root.add_widget(self.l_dist)
        root.add_widget(self.l_speed)
        self.hearts = HeartsWidget(size_hint=(.24, .035), pos_hint={'right': .97, 'top': .91})
        root.add_widget(self.hearts)
        self.root_layout = root
        self.add_widget(root)

    # ---- lifecycle ---------------------------------------------------------
    def new_run(self, level):
        self.level = level
        self.hide_overlay()
        self.paused = False
        self._ending = False
        self.app.tilt_queue[:] = []
        self.gw.enabled = True
        self.gw.new_world(level)
        self._last = {}
        self.update_hud(force=True)

    def on_enter(self, *a):
        if self._ev is None:
            self._ev = Clock.schedule_interval(self.tick, 1 / 60.0)

    def on_leave(self, *a):
        if self._ev:
            self._ev.cancel()
            self._ev = None

    # ---- input ---------------------------------------------------------------
    def apply(self, g):
        wd = self.gw.world
        if wd is None or self.paused or wd.state != 'run':
            return
        if g == 'left':
            wd.move(-1)
        elif g == 'right':
            wd.move(1)
        elif g == 'up':
            wd.jump()
        elif g == 'down':
            wd.slide()

    # ---- main loop -----------------------------------------------------------
    def tick(self, dt):
        wd = self.gw.world
        if self.paused or wd is None:
            return
        dt = min(dt, 0.05)
        q = self.app.tilt_queue
        if self.app.save['control'] in ('tilt', 'both'):
            while q:
                g = q.pop(0)
                if g in ('left', 'right'):
                    self.apply(g)
        else:
            del q[:]
        wd.update(dt)
        for e in wd.pop_events():
            self.app.audio.play(e)
        self.gw.draw()
        self.update_hud()
        if wd.state != 'run' and not self._ending:
            self._ending = True
            Clock.schedule_once(self._finish, 0.9 if wd.state == 'dead' else 0.5)

    def _finish(self, dt):
        wd = self.gw.world
        if self.paused or wd is None:
            return
        self.app.finish_run(wd.result())

    def _set(self, key, widget, text):
        if self._last.get(key) != text:
            self._last[key] = text
            widget.text = text

    def update_hud(self, force=False):
        wd = self.gw.world
        if wd is None:
            return
        self._set('s', self.l_score, '{:,}'.format(wd.score))
        self._set('m', self.l_mult, 'x%d' % wd.multiplier)
        self._set('c', self.l_coins, str(wd.coins))
        self._set('d', self.l_dist, '%d m' % int(wd.dist))
        self._set('v', self.l_speed, '%d km/h' % int(wd.speed * 3.6))
        if self.hearts.max_hp != wd.max_hp:
            self.hearts.max_hp = wd.max_hp
        if self.hearts.hp != max(0, wd.hp):
            self.hearts.hp = max(0, wd.hp)

    # ---- pause -----------------------------------------------------------------
    def pause(self):
        wd = self.gw.world
        if self.paused or wd is None or wd.state != 'run':
            return
        self.paused = True
        self.show_overlay()

    def resume(self):
        self.hide_overlay()
        self.paused = False

    def toggle_pause(self):
        if self.paused:
            self.resume()
        else:
            self.pause()

    def restart(self):
        self.new_run(self.level)

    def hide_overlay(self):
        if self.overlay is not None:
            self.root_layout.remove_widget(self.overlay)
            self.overlay = None

    def show_overlay(self):
        T = self.T
        ov = Overlay(size_hint=(1, 1))
        ov.add_widget(GlassPanel(size_hint=(.78, .50), pos_hint={'center_x': .5, 'center_y': .5}))
        title = FloatLayout(size_hint=(.70, .085), pos_hint={'center_x': .5, 'y': .64})
        title.add_widget(GlassPanel(size_hint=(1, 1), radius_frac=.25, fill=[.02, .06, .24, 1]))
        title.add_widget(IconWidget(name='pause', size_hint=(.16, .7), pos_hint={'x': .06, 'center_y': .5}))
        title.add_widget(FLabel(text=T('paused'), bold=True, italic=True, frac=.62, size_hint=(.6, .8),
                                pos_hint={'x': .26, 'center_y': .5}))
        ov.add_widget(title)
        items = [('resume', 'play', 'green', self.resume, .545),
                 ('restart', 'restart', 'blue', self.restart, .455),
                 ('settings', 'gear', 'blue', lambda: self.app.open_settings('game'), .365),
                 ('home', 'home', 'blue', lambda: self.app.go_home(), .275)]
        for key, icon, style, fn, y in items:
            b = NeonButton(text=T(key), icon=icon, style=style, fs=.40, size_hint=(.62, .072), pos_hint={'center_x': .5, 'y': y})
            b.bind(on_release=lambda *a, f=fn: f())
            ov.add_widget(b)
        self.overlay = ov
        self.root_layout.add_widget(ov)


class Confetti(Widget):
    COLORS = [(1, .85, .2), (1, .6, .1), (1, .95, .6), (1, .4, .3), (.4, .9, 1)]

    def __init__(self, **kw):
        super().__init__(**kw)
        self.p = []
        self._ev = None

    def start(self):
        self.stop()
        self.p = [[random.random(), random.random() * 1.2, random.uniform(.06, .25), random.choice(self.COLORS),
                   random.uniform(0, 6)] for _ in range(60)]
        self._ev = Clock.schedule_interval(self._u, 1 / 30.0)

    def stop(self):
        if self._ev:
            self._ev.cancel()
            self._ev = None
        self.canvas.clear()

    def _u(self, dt):
        self.canvas.clear()
        w, h = self.size
        with self.canvas:
            for p in self.p:
                p[1] -= p[2] * dt
                p[4] += dt * 3
                if p[1] < -0.05:
                    p[1] = 1.05
                    p[0] = random.random()
                Color(p[3][0], p[3][1], p[3][2], 0.9)
                Rectangle(pos=(self.x + (p[0] + 0.01 * math.sin(p[4])) * w, self.y + p[1] * h), size=(w * .012, w * .02))


class Burst(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._d, size=self._d)

    def _d(self, *a):
        self.canvas.clear()
        with self.canvas:
            for i, al in enumerate((.05, .07, .10, .14)):
                Color(1, .8, .2, al)
                g = (4 - i) * self.width * .12
                Ellipse(pos=(self.center_x - g, self.center_y - g), size=(g * 2, g * 2))


class ResultScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, 'result', **kw)
        self.res = None
        self.new_best = False
        self.best = 0
        self.confetti = None

    def show(self, res, new_best, best):
        self.res, self.new_best, self.best = res, new_best, best
        self.build()

    def on_enter(self, *a):
        if self.confetti is not None and self.res and self.res['won']:
            self.confetti.start()

    def on_leave(self, *a):
        if self.confetti is not None:
            self.confetti.stop()

    def build(self):
        self.clear_widgets()
        app, T, r = self.app, self.T, self.res
        root = FloatLayout()
        root.add_widget(CityBackground(mode='select', quality=app.save['quality']))
        won = r['won']
        if won:
            root.add_widget(Burst(size_hint=(.9, .5), pos_hint={'center_x': .5, 'center_y': .70}))
            root.add_widget(IconWidget(name='trophy', size_hint=(.62, .32), pos_hint={'center_x': .5, 'top': .92}, scale=.95))
        else:
            root.add_widget(FLabel(text=T('score'), frac=.5, color=ICE, size_hint=(.6, .05), pos_hint={'center_x': .5, 'top': .86}))
            root.add_widget(FLabel(text='{:,}'.format(r['score']), bold=True, italic=True, frac=.9, color=GOLD,
                                   outline_width=_ow(), outline_color=(.4, .15, 0, 1),
                                   size_hint=(.9, .11), pos_hint={'center_x': .5, 'top': .80}))
        rb = FloatLayout(size_hint=(.92, .095), pos_hint={'center_x': .5, 'y': .52 if won else .60})
        rb.add_widget(GlassPanel(size_hint=(1, 1), radius_frac=.18,
                                 fill=[.62, .05, .10, 1] if won else [.30, .03, .08, 1], border=[1, .8, .3, 1] if won else [1, .35, .35, 1]))
        rb.add_widget(FLabel(text=T('level_complete') if won else T('game_over'), bold=True, italic=True, frac=.62,
                             color=GOLD if won else (1, .85, .85, 1), outline_width=_ow(), outline_color=(.25, 0, 0, 1),
                             size_hint=(1, .9), pos_hint={'center_x': .5, 'center_y': .5}))
        root.add_widget(rb)
        lines = []
        if won:
            lines.append((T('score'), '{:,}'.format(r['score']), 'trophy'))
        else:
            lines.append((T('best'), '{:,}'.format(self.best) + ('  NEW!' if self.new_best else ''), 'crown'))
        lines.append((T('coins'), str(r['coins']), 'coin'))
        lines.append((T('distance'), '%d m' % r['distance'], 'bolt'))
        y0 = .45 if won else .50
        for i, (k, v, ic) in enumerate(lines):
            yy = y0 - i * .065
            root.add_widget(IconWidget(name=ic, size_hint=(.08, .05), pos_hint={'x': .16, 'y': yy}))
            root.add_widget(FLabel(text='%s:' % k, frac=.52, halign='left', color=ICE, size_hint=(.30, .05), pos_hint={'x': .26, 'y': yy}))
            root.add_widget(FLabel(text=v, bold=True, frac=.56, halign='left', size_hint=(.40, .05), pos_hint={'x': .50, 'y': yy}))
        if won:
            for i in range(3):
                lit = i < r['stars']
                root.add_widget(IconWidget(name='star', tint=[1, .85, .2, 1] if lit else [.3, .33, .5, 1],
                                           size_hint=(.24, .09), pos_hint={'x': .15 + i * .24, 'y': .205 + (.025 if i == 1 else 0)}))
        home = NeonButton(text=T('home'), icon='home', style='blue', fs=.40, size_hint=(.42, .085), pos_hint={'x': .06, 'y': .06})
        home.bind(on_release=lambda *a: app.go_home())
        if won:
            nxt = NeonButton(text=T('next'), icon='next', style='gold', fs=.42, size_hint=(.42, .085), pos_hint={'x': .52, 'y': .06})
            nxt.bind(on_release=lambda *a: app.start_game(r['level'] + 1))
        else:
            nxt = NeonButton(text=T('restart'), icon='restart', style='gold', fs=.38, size_hint=(.42, .085), pos_hint={'x': .52, 'y': .06})
            nxt.bind(on_release=lambda *a: app.start_game(r['level']))
        root.add_widget(home)
        root.add_widget(nxt)
        self.confetti = Confetti(size_hint=(1, 1))
        root.add_widget(self.confetti)
        self.add_widget(root)
