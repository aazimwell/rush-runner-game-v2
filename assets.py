"""Audio manager. All sounds are bundled files (assets/sounds/*.wav) - no network."""
import os

from kivy.core.audio import SoundLoader

BASE = os.path.dirname(os.path.abspath(__file__))
SND = os.path.join(BASE, 'assets', 'sounds')
NAMES = ['coin', 'diamond', 'hit', 'jump', 'slide', 'lane', 'click', 'win', 'lose']

audio = None   # set by main.py


def play(name):
    if audio is not None:
        audio.play(name)


class Audio:
    def __init__(self, save):
        self.save = save
        self.sounds = {}
        self.music = None

    def load(self):
        for n in NAMES:
            try:
                s = SoundLoader.load(os.path.join(SND, n + '.wav'))
                if s:
                    self.sounds[n] = s
            except Exception:
                pass
        try:
            self.music = SoundLoader.load(os.path.join(SND, 'music.wav'))
            if self.music:
                self.music.loop = True
                self.music.volume = 0.45
        except Exception:
            self.music = None

    def play(self, name):
        if not self.save['sfx']:
            return
        s = self.sounds.get(name)
        if s:
            try:
                s.stop()
                s.play()
            except Exception:
                pass

    def start_music(self):
        if self.music and self.save['music']:
            try:
                if self.music.state != 'play':
                    self.music.play()
            except Exception:
                pass

    def stop_music(self):
        if self.music:
            try:
                self.music.stop()
            except Exception:
                pass

    def refresh_music(self):
        if self.save['music']:
            self.start_music()
        else:
            self.stop_music()
