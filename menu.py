"""Home, Character select, Settings and High-score screens."""
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.properties import NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

import characters
import settings as cfg
from ui_components import (ArrowButton, CityBackground, FLabel, GlassPanel, IconWidget, NeonButton,
                           NeonToggle, RunnerFigure, TiltBar, gradient)

GOLD = (1.0, 0.80, 0.12, 1)
ICE = (0.82, 0.92, 1.0, 1)


def _ow():
    return max(2, int(Window.height * 0.0035))


def pill(icon, text, pos_hint, size_hint):
    f = FloatLayout(size_hint=size_hint, pos_hint=pos_hint)
    f.add_widget(GlassPanel(size_hint=(1, 1), radius_frac=0.30))
    f.add_widget(IconWidget(name=icon, size_hint=(.22, .86), pos_hint={'x': .03, 'center_y': .5}))
    f.add_widget(FLabel(text=text, bold=True, frac=.58, size_hint=(.66, .8), pos_hint={'x': .28, 'center_y': .5}))
    return f


class BaseScreen(Screen):
    def __init__(self, app, name, **kw):
        super().__init__(name=name, **kw)
        self.app = app

    def T(self, key):
        return self.app.T(key)


class HomeScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, 'home', **kw)

    def on_pre_enter(self, *a):
        self.build()

    def build(self):
        self.clear_widgets()
        app, save, T = self.app, self.app.save, self.T
        root = FloatLayout()
        root.add_widget(CityBackground(mode='home', quality=save['quality']))
        root.add_widget(RunnerFigure(kind=save['selected'], front=False, animate=True,
                                     size_hint=(.40, .40), pos_hint={'x': .56, 'y': .285}))
        # logo
        root.add_widget(FLabel(text='RUSH', bold=True, italic=True, frac=.92, halign='left',
                               color=(.88, .95, 1, 1), outline_width=_ow(), outline_color=(.1, .35, .95, 1),
                               size_hint=(.64, .085), pos_hint={'x': .035, 'top': .925}))
        root.add_widget(FLabel(text='RUNNER', bold=True, italic=True, frac=.95, halign='left',
                               color=GOLD, outline_width=_ow(), outline_color=(.55, .2, .0, 1),
                               size_hint=(.82, .105), pos_hint={'x': .035, 'top': .843}))
        sub = FloatLayout(size_hint=(.56, .036), pos_hint={'x': .05, 'top': .735})
        sub.add_widget(GlassPanel(size_hint=(1, 1), radius_frac=.25, fill=[0.02, 0.03, 0.10, 0.92]))
        sub.add_widget(FLabel(text=T('subtitle'), bold=True, italic=True, frac=.55, color=ICE, size_hint=(1, 1)))
        root.add_widget(sub)
        root.add_widget(FLabel(text=T('tagline'), italic=True, bold=True, frac=.24, halign='right',
                               color=GOLD, size_hint=(.40, .075), pos_hint={'right': .97, 'y': .685}))
        # resources
        root.add_widget(pill('coin', '{:,}'.format(save['coins']), {'x': .30, 'top': .985}, (.26, .04)))
        root.add_widget(pill('diamond', '{:,}'.format(save['diamonds']), {'x': .58, 'top': .985}, (.22, .04)))
        crown = NeonButton(icon='crown', style='blue', size_hint=(.13, .04), pos_hint={'x': .84, 'top': .985})
        crown.bind(on_release=lambda *a: app.go('scores'))
        root.add_widget(crown)
        # menu column
        play = NeonButton(text=T('play'), icon='play', style='gold', fs=.46,
                          size_hint=(.58, .092), pos_hint={'x': .04, 'y': .300})
        play.bind(on_release=lambda *a: app.start_game(save['level']))
        root.add_widget(play)
        items = [('character', 'user', lambda: app.go('select'), .225),
                 ('settings', 'gear', lambda: app.open_settings('home'), .160),
                 ('high_score', 'trophy', lambda: app.go('scores'), .095),
                 ('quit', 'exit', lambda: app.stop(), .030)]
        for key, icon, fn, y in items:
            b = NeonButton(text=T(key), icon=icon, style='blue', fs=.40,
                           size_hint=(.52, .055), pos_hint={'x': .04, 'y': y})
            b.bind(on_release=lambda *a, f=fn: f())
            root.add_widget(b)
        self.add_widget(root)


class GlowPlatform(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._d, size=self._d)

    def _d(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        self.canvas.clear()
        with self.canvas:
            for i, al in enumerate((.10, .16, .26)):
                Color(.1, .5, 1, al)
                g = (3 - i) * w * .03
                Ellipse(pos=(x - g, y - g * .4), size=(w + g * 2, h + g * .8))
            Color(.03, .08, .25, 1)
            Ellipse(pos=(x, y), size=(w, h))
            Color(.2, .85, 1, 1)
            Line(ellipse=(x, y, w, h), width=2.4)
            Line(ellipse=(x + w * .08, y + h * .08, w * .84, h * .84), width=1.4)
            Color(.2, .85, 1, .35)
            Line(ellipse=(x + w * .2, y + h * .2, w * .6, h * .6), width=1.2)


class StatBar(Widget):
    value = NumericProperty(.5)

    def __init__(self, color=(.2, .8, 1, 1), **kw):
        super().__init__(**kw)
        self.color = color
        self.bind(pos=self._d, size=self._d, value=self._d)

    def _d(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        self.canvas.clear()
        with self.canvas:
            Color(.1, .14, .28, 1)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[h / 2])
            Color(*self.color)
            RoundedRectangle(pos=(x, y), size=(max(h, w * max(0.0, min(1.0, self.value))), h), radius=[h / 2])


class Thumb(ButtonBehavior, FloatLayout):
    def __init__(self, kind, selected, locked, **kw):
        super().__init__(**kw)
        self.selected = selected
        self.add_widget(RunnerFigure(kind=kind, front=True, dim=locked, size_hint=(.92, .88),
                                     pos_hint={'center_x': .5, 'y': .06}))
        if locked:
            self.add_widget(IconWidget(name='lock', size_hint=(.4, .4), pos_hint={'center_x': .5, 'center_y': .5}))
        self.bind(pos=self._d, size=self._d)
        self._d()

    def _d(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            top, bot = ((.30, .22, .02, 1), (.12, .08, .0, 1)) if self.selected else ((.05, .12, .32, 1), (.02, .04, .16, 1))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.width * .14], texture=gradient(top, bot))
            if self.selected:
                Color(1.0, .8, .15, 1)
            else:
                Color(.2, .6, 1, .9)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.width * .14), width=2.6 if self.selected else 1.4)


class SelectScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, 'select', **kw)
        self.idx = 0

    def on_pre_enter(self, *a):
        ids = [c['id'] for c in characters.CHARACTERS]
        sel = self.app.save['selected']
        self.idx = ids.index(sel) if sel in ids else 0
        self.build()

    def step(self, d):
        self.idx = (self.idx + d) % len(characters.CHARACTERS)
        self.build()

    def choose(self):
        c = characters.CHARACTERS[self.idx]
        save = self.app.save
        if c['id'] not in save['unlocked']:
            return
        save['selected'] = c['id']
        save.save()
        self.app.go('home')

    def unlock(self):
        c = characters.CHARACTERS[self.idx]
        save = self.app.save
        if c['id'] in save['unlocked'] or save['coins'] < c['cost']:
            return
        save['coins'] -= c['cost']
        save['unlocked'].append(c['id'])
        save['selected'] = c['id']
        save.save()
        self.build()

    def build(self):
        self.clear_widgets()
        app, save, T = self.app, self.app.save, self.T
        c = characters.CHARACTERS[self.idx]
        unlocked = c['id'] in save['unlocked']
        root = FloatLayout()
        root.add_widget(CityBackground(mode='select', quality=save['quality']))
        back = NeonButton(icon='back', style='blue', size_hint=(.13, .055), pos_hint={'x': .03, 'top': .975})
        back.bind(on_release=lambda *a: app.go('home'))
        root.add_widget(back)
        root.add_widget(FLabel(text=T('character_select'), bold=True, italic=True, frac=.62, color=(.9, .96, 1, 1),
                               size_hint=(.74, .05), pos_hint={'x': .20, 'top': .972}))
        root.add_widget(GlowPlatform(size_hint=(.58, .075), pos_hint={'x': .36, 'y': .405}))
        root.add_widget(RunnerFigure(kind=c['id'], front=True, animate=True, dim=not unlocked,
                                     size_hint=(.50, .44), pos_hint={'x': .40, 'y': .43}))
        for i, ch in enumerate(characters.CHARACTERS):
            t = Thumb(ch['id'], i == self.idx, ch['id'] not in save['unlocked'],
                      size_hint=(.20, .105), pos_hint={'x': .03, 'top': .86 - i * .118})
            t.bind(on_release=lambda w, i=i: self._pick(i))
            root.add_widget(t)
        root.add_widget(GlassPanel(size_hint=(.92, .215), pos_hint={'x': .04, 'y': .175}))
        root.add_widget(FLabel(text=c['name'], bold=True, italic=True, frac=.72, halign='left',
                               size_hint=(.52, .05), pos_hint={'x': .08, 'y': .33}))
        root.add_widget(FLabel(text=c['desc'], frac=.30, halign='left', color=ICE,
                               size_hint=(.50, .07), pos_hint={'x': .08, 'y': .262}))
        ab = c['ability'] if unlocked else '%s - %d %s' % (T('locked'), c['cost'], T('coins'))
        root.add_widget(FLabel(text=ab, frac=.36, halign='left', color=GOLD if unlocked else (1, .5, .5, 1),
                               size_hint=(.50, .05), pos_hint={'x': .08, 'y': .20}))
        rows = [('heart', T('health'), c['health'] / characters.MAX_HEALTH, (.15, .8, 1, 1), .345),
                ('bolt', T('speed'), c['speed'] / characters.MAX_SPEED, (1, .8, .1, 1), .288),
                ('magnet', T('magnet'), c['magnet'] / characters.MAX_MAGNET, (.7, .3, 1, 1), .231)]
        for icon, label, val, color, y in rows:
            root.add_widget(IconWidget(name=icon, size_hint=(.06, .036), pos_hint={'x': .58, 'y': y}))
            root.add_widget(FLabel(text=label, frac=.40, halign='left', size_hint=(.17, .036), pos_hint={'x': .65, 'y': y}))
            root.add_widget(StatBar(value=val, color=color, size_hint=(.13, .013), pos_hint={'x': .82, 'y': y + .011}))
        prev = NeonButton(text=T('previous'), icon='left', style='blue', fs=.36, size_hint=(.44, .06), pos_hint={'x': .04, 'y': .105})
        prev.bind(on_release=lambda *a: self.step(-1))
        nxt = NeonButton(text=T('next'), icon='right', style='blue', fs=.36, size_hint=(.44, .06), pos_hint={'x': .52, 'y': .105})
        nxt.bind(on_release=lambda *a: self.step(1))
        bk = NeonButton(text=T('back'), style='purple', fs=.38, size_hint=(.28, .075), pos_hint={'x': .04, 'y': .02})
        bk.bind(on_release=lambda *a: app.go('home'))
        if unlocked:
            sel = NeonButton(text=T('selected') if save['selected'] == c['id'] else T('select'),
                             icon='check', style='gold', fs=.40, size_hint=(.60, .075), pos_hint={'x': .36, 'y': .02})
            sel.bind(on_release=lambda *a: self.choose())
        else:
            sel = NeonButton(text='%s %d' % (T('unlock'), c['cost']), icon='coin',
                             style='gold' if save['coins'] >= c['cost'] else 'blue', fs=.36,
                             size_hint=(.60, .075), pos_hint={'x': .36, 'y': .02})
            sel.disabled = save['coins'] < c['cost']
            sel.bind(on_release=lambda *a: self.unlock())
        for w in (prev, nxt, bk, sel):
            root.add_widget(w)
        self.add_widget(root)

    def _pick(self, i):
        self.idx = i
        self.build()


class SettingsScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, 'settings', **kw)
        self.return_to = 'home'
        self._ev = None
        self.bar = None
        self.status = None

    def on_pre_enter(self, *a):
        self.build()

    def on_enter(self, *a):
        self._ev = Clock.schedule_interval(self._upd, 1 / 15.0)

    def on_leave(self, *a):
        if self._ev:
            self._ev.cancel()
            self._ev = None

    def _upd(self, dt):
        app = self.app
        if self.bar is not None:
            self.bar.value = app.tilt.value
        if self.status is not None:
            if app.save['control'] == 'touch':
                self.status.text = '%s: OFF (Touch only)' % self.T('tilt_sensor')
            elif app.sensor.available:
                self.status.text = self.T('sensor_ok')
            else:
                self.status.text = self.T('no_sensor')

    def _change(self, key, step):
        app = self.app
        cfg.cycle(app.save, key, step)
        if key == 'control':
            app.sync_sensor()
        elif key == 'sensitivity':
            app.apply_sensitivity()
        self.build()

    def build(self):
        self.clear_widgets()
        app, save, T = self.app, self.app.save, self.T
        root = FloatLayout()
        root.add_widget(CityBackground(mode='select', quality=save['quality']))
        root.add_widget(GlassPanel(size_hint=(.88, .90), pos_hint={'x': .06, 'y': .05}))
        root.add_widget(IconWidget(name='gear', size_hint=(.10, .06), pos_hint={'x': .10, 'top': .94}))
        root.add_widget(FLabel(text=T('settings'), bold=True, italic=True, frac=.62, halign='left',
                               size_hint=(.5, .06), pos_hint={'x': .22, 'top': .94}))
        y = .80

        def row_base(icon, label):
            root.add_widget(IconWidget(name=icon, size_hint=(.07, .05), pos_hint={'x': .10, 'y': y}))
            root.add_widget(FLabel(text=label, frac=.38, halign='left', size_hint=(.34, .05), pos_hint={'x': .18, 'y': y}))

        def toggle(icon, label, key):
            row_base(icon, label)
            t = NeonToggle(value=bool(save[key]), size_hint=(.17, .036), pos_hint={'right': .88, 'y': y + .007})
            t.bind(on_toggle=lambda w, v, k=key: self._toggle(k, v))
            root.add_widget(t)

        def selector(icon, label, key, text):
            row_base(icon, label)
            l = ArrowButton(direction=-1, size_hint=(.06, .045), pos_hint={'x': .50, 'y': y + .002})
            l.bind(on_release=lambda *a, k=key: self._change(k, -1))
            r = ArrowButton(direction=1, size_hint=(.06, .045), pos_hint={'x': .83, 'y': y + .002})
            r.bind(on_release=lambda *a, k=key: self._change(k, 1))
            root.add_widget(l)
            root.add_widget(FLabel(text=text, bold=True, frac=.40, size_hint=(.27, .05), pos_hint={'x': .56, 'y': y}))
            root.add_widget(r)

        toggle('music', T('music'), 'music')
        y -= .088
        toggle('speaker', T('sfx'), 'sfx')
        y -= .088
        selector('monitor', T('graphics'), 'quality', save['quality'])
        y -= .088
        selector('gamepad', T('control_style'), 'control', cfg.CONTROL_LABEL[save['control']])
        y -= .088
        selector('phone', T('sensitivity'), 'sensitivity', save['sensitivity'])
        y -= .088
        selector('globe', T('language'), 'language', save['language'])
        self.status = FLabel(text='', frac=.42, color=ICE, size_hint=(.76, .035), pos_hint={'x': .12, 'y': .295})
        root.add_widget(self.status)
        self.bar = TiltBar(limit=5.0, size_hint=(.76, .028), pos_hint={'x': .12, 'y': .255})
        root.add_widget(self.bar)
        self.msg = FLabel(text='', frac=.5, color=GOLD, size_hint=(.76, .03), pos_hint={'x': .12, 'y': .222})
        root.add_widget(self.msg)
        cal = NeonButton(text=T('calibrate'), icon='phone', style='blue', fs=.38, size_hint=(.76, .065), pos_hint={'x': .12, 'y': .145})
        cal.bind(on_release=lambda *a: self._calibrate())
        root.add_widget(cal)
        bk = NeonButton(text=T('back'), icon='back', style='purple', fs=.40, size_hint=(.50, .07), pos_hint={'x': .25, 'y': .06})
        bk.bind(on_release=lambda *a: app.go(self.return_to))
        root.add_widget(bk)
        self.add_widget(root)

    def _toggle(self, key, v):
        self.app.save[key] = bool(v)
        self.app.save.save()
        if key == 'music':
            self.app.audio.refresh_music()

    def _calibrate(self):
        ok = self.app.calibrate()
        self.msg.text = self.T('calibrated') if ok else self.T('no_sensor')


class ScoresScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, 'scores', **kw)

    def on_pre_enter(self, *a):
        self.build()

    def build(self):
        self.clear_widgets()
        app, save, T = self.app, self.app.save, self.T
        root = FloatLayout()
        root.add_widget(CityBackground(mode='select', quality=save['quality']))
        back = NeonButton(icon='back', style='blue', size_hint=(.13, .055), pos_hint={'x': .03, 'top': .975})
        back.bind(on_release=lambda *a: app.go('home'))
        root.add_widget(back)
        root.add_widget(FLabel(text=T('high_score'), bold=True, italic=True, frac=.62, color=(.9, .96, 1, 1),
                               size_hint=(.7, .05), pos_hint={'x': .2, 'top': .972}))
        root.add_widget(GlassPanel(size_hint=(.88, .36), pos_hint={'x': .06, 'y': .56}))
        root.add_widget(IconWidget(name='trophy', size_hint=(.30, .15), pos_hint={'center_x': .5, 'top': .90}))
        root.add_widget(FLabel(text='{:,}'.format(save['high_score']), bold=True, italic=True, frac=.9, color=GOLD,
                               outline_width=_ow(), outline_color=(.4, .15, 0, 1),
                               size_hint=(.8, .075), pos_hint={'center_x': .5, 'y': .66}))
        stats = '%s: %d m     %s: %s     %s: %d     %s: %s' % (
            T('distance'), save['best_distance'], T('coins'), '{:,}'.format(save['coins']),
            T('level'), save['level'], 'Gems', '{:,}'.format(save['diamonds']))
        root.add_widget(FLabel(text=stats, frac=.34, color=ICE, size_hint=(.84, .06), pos_hint={'center_x': .5, 'y': .58}))
        root.add_widget(GlassPanel(size_hint=(.88, .45), pos_hint={'x': .06, 'y': .07}, border=[1, .8, .2, 1]))
        root.add_widget(IconWidget(name='crown', size_hint=(.10, .05), pos_hint={'x': .10, 'top': .50}))
        root.add_widget(FLabel(text=T('achievements'), bold=True, italic=True, frac=.55, halign='left', color=GOLD,
                               size_hint=(.6, .05), pos_hint={'x': .22, 'top': .50}))
        ach = [('Run 1,000 m in one go', save['best_distance'] >= 1000),
               ('Collect 1,000 coins in total', save['total_coins'] >= 1000),
               ('Score 10,000 points', save['high_score'] >= 10000),
               ('Unlock every runner', len(save['unlocked']) >= len(characters.CHARACTERS)),
               ('Reach level 5', save['level'] >= 5)]
        for i, (txt, done) in enumerate(ach):
            yy = .385 - i * .066
            root.add_widget(IconWidget(name='star', tint=[1, .85, .2, 1] if done else [.3, .35, .5, 1],
                                       size_hint=(.07, .045), pos_hint={'x': .10, 'y': yy}))
            root.add_widget(FLabel(text=txt, frac=.42, halign='left', color=(1, 1, 1, 1) if done else (.6, .68, .85, 1),
                                   size_hint=(.68, .045), pos_hint={'x': .20, 'y': yy}))
        self.add_widget(root)
