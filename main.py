"""RUSH RUNNER - ENDLESS ADVENTURE  (Kivy + Buildozer, fully offline)."""
import os
import time

os.environ.setdefault('KIVY_NO_ARGS', '1')

from kivy.config import Config  # noqa: E402
from kivy.utils import platform  # noqa: E402

if platform != 'android':          # desktop preview only
    Config.set('graphics', 'width', '450')
    Config.set('graphics', 'height', '800')
    Config.set('graphics', 'resizable', '0')

from kivy.app import App  # noqa: E402
from kivy.clock import Clock  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.uix.label import Label  # noqa: E402
from kivy.uix.screenmanager import FadeTransition, ScreenManager  # noqa: E402

import assets  # noqa: E402
import settings as cfg  # noqa: E402
from controls import TiltController  # noqa: E402
from game import GameScreen, ResultScreen  # noqa: E402
from menu import HomeScreen, ScoresScreen, SelectScreen, SettingsScreen  # noqa: E402
from save_manager import SaveManager  # noqa: E402
from sensors import AccelSensor, exclude_system_gestures  # noqa: E402


class RushRunnerApp(App):
    def build(self):
        self.title = 'Rush Runner'
        Window.clearcolor = (0.02, 0.03, 0.10, 1)
        self.save = SaveManager(os.path.join(self.user_data_dir, 'save.json')).load()
        self.audio = assets.Audio(self.save)
        assets.audio = self.audio
        self.audio.load()
        self.sensor = AccelSensor()
        self.tilt = TiltController(offset=float(self.save['tilt_offset']))
        self.tilt_queue = []
        self.apply_sensitivity()
        self._quit_t = 0.0
        self.sm = ScreenManager(transition=FadeTransition(duration=0.10))
        self.home = HomeScreen(self)
        self.select = SelectScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.scores = ScoresScreen(self)
        self.game = GameScreen(self)
        self.result = ResultScreen(self)
        for s in (self.home, self.select, self.settings_screen, self.scores, self.game, self.result):
            self.sm.add_widget(s)
        self.sm.current = 'home'
        Window.bind(on_keyboard=self.on_key)
        return self.sm

    def on_start(self):
        self.audio.refresh_music()
        self.sync_sensor()
        exclude_system_gestures()
        Clock.schedule_interval(self._sensor_tick, 1 / 60.0)

    # ---- helpers -------------------------------------------------------------
    def T(self, key):
        return cfg.tr(self.save['language'], key)

    def go(self, name):
        self.sm.current = name

    def go_home(self):
        self.game.hide_overlay()
        self.game.paused = False
        self.go('home')

    def open_settings(self, return_to):
        self.settings_screen.return_to = return_to
        self.go('settings')

    def start_game(self, level):
        self.game.new_run(max(1, int(level)))
        self.go('game')

    def finish_run(self, res):
        s = self.save
        s['coins'] += res['coins']
        s['diamonds'] += res['diamonds']
        s['total_coins'] += res['coins']
        new_best = res['score'] > s['high_score']
        if new_best:
            s['high_score'] = res['score']
        s['best_distance'] = max(s['best_distance'], res['distance'])
        if res['won']:
            s['level'] = max(s['level'], res['level'] + 1)
        s.save()
        self.audio.play('win' if res['won'] else 'lose')
        self.result.show(res, new_best, s['high_score'])
        self.go('result')

    # ---- sensors ---------------------------------------------------------------
    def apply_sensitivity(self):
        lv = self.save['sensitivity']
        self.tilt.configure(cfg.TILT_THRESH.get(lv, 2.0), cfg.TILT_DEAD.get(lv, 0.9))

    def sync_sensor(self):
        if self.save['control'] in ('tilt', 'both'):
            self.sensor.start()
            self.tilt.reset()
        else:
            self.sensor.stop()
            self.tilt.reset()
        del self.tilt_queue[:]

    def _sensor_tick(self, dt):
        v = self.sensor.read()
        if not v:
            return
        g = self.tilt.feed(v[0], time.time())
        if g and self.sm.current == 'game' and len(self.tilt_queue) < 4:
            self.tilt_queue.append(g)

    def calibrate(self):
        if self.save['control'] == 'touch':
            return False
        if not self.sensor.enabled:
            self.sensor.start()
        if not self.tilt.calibrate():
            return False
        self.save['tilt_offset'] = float(self.tilt.offset)
        self.save.save()
        return True

    # ---- android lifecycle / back button ------------------------------------------
    def on_pause(self):
        self.audio.stop_music()
        self.sensor.stop()
        if self.sm.current == 'game':
            self.game.pause()
        self.save.save()
        return True

    def on_resume(self):
        self.audio.refresh_music()
        self.sync_sensor()

    def on_stop(self):
        self.save.save()

    def toast(self, text):
        lbl = Label(text=text, size_hint=(None, None), size=(Window.width * 0.8, Window.height * 0.05),
                    pos=(Window.width * 0.1, Window.height * 0.12), font_size=Window.height * 0.022,
                    color=(1, 1, 1, 1))
        Window.add_widget(lbl)
        Clock.schedule_once(lambda dt: Window.remove_widget(lbl), 2.0)

    def on_key(self, window, key, *args):
        if key != 27:           # Android Back / Esc
            return False
        cur = self.sm.current
        if cur == 'game':
            self.game.toggle_pause()
        elif cur == 'settings':
            self.go(self.settings_screen.return_to)
        elif cur in ('select', 'scores', 'result'):
            self.go_home()
        else:
            now = time.time()
            if now - self._quit_t < 2.0:
                self.stop()
            else:
                self._quit_t = now
                self.toast(self.T('press_back_again'))
        return True


if __name__ == '__main__':
    RushRunnerApp().run()
