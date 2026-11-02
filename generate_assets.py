"""Generates ALL bundled audio + the app icon from scratch (original, license-free).
Standard library only. Safe to run repeatedly:  python generate_assets.py
"""
import math
import os
import random
import struct
import wave
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SND = os.path.join(HERE, 'assets', 'sounds')
ICO = os.path.join(HERE, 'assets', 'icons')
RATE = 22050


def _write_wav(name, samples):
    os.makedirs(SND, exist_ok=True)
    with wave.open(os.path.join(SND, name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h', max(-32767, min(32767, int(s * 32767))))
                               for s in samples))


def _tone(freq, dur, vol=0.5, kind='sine', slide=0.0, decay=4.0):
    n = int(RATE * dur)
    out = []
    ph = 0.0
    for i in range(n):
        t = i / RATE
        f = freq + slide * t
        ph += 2 * math.pi * f / RATE
        if kind == 'sine':
            s = math.sin(ph)
        elif kind == 'square':
            s = 1.0 if math.sin(ph) >= 0 else -1.0
        elif kind == 'tri':
            s = 2 / math.pi * math.asin(math.sin(ph))
        else:
            s = random.uniform(-1, 1)
        env = math.exp(-decay * t / dur) * min(1.0, i / 120.0)
        out.append(s * vol * env)
    return out


def make_sounds():
    random.seed(1)
    _write_wav('coin.wav', _tone(988, 0.07, 0.45, 'square', decay=1.0) +
               _tone(1319, 0.16, 0.45, 'square', decay=4.0))
    _write_wav('diamond.wav', _tone(1175, 0.08, 0.4, 'tri') + _tone(1568, 0.08, 0.4, 'tri') +
               _tone(2093, 0.22, 0.4, 'tri', decay=5.0))
    _write_wav('hit.wav', _tone(140, 0.35, 0.7, 'noise', decay=6.0))
    _write_wav('jump.wav', _tone(300, 0.20, 0.4, 'sine', slide=900, decay=2.5))
    _write_wav('slide.wav', _tone(500, 0.22, 0.3, 'noise', decay=3.0))
    _write_wav('lane.wav', _tone(420, 0.07, 0.25, 'tri', slide=500, decay=3.0))
    _write_wav('click.wav', _tone(700, 0.06, 0.4, 'square', decay=5.0))
    _write_wav('win.wav', _tone(523, 0.14, 0.4, 'tri') + _tone(659, 0.14, 0.4, 'tri') +
               _tone(784, 0.14, 0.4, 'tri') + _tone(1047, 0.45, 0.45, 'tri', decay=3.0))
    _write_wav('lose.wav', _tone(392, 0.2, 0.45, 'tri') + _tone(330, 0.2, 0.45, 'tri') +
               _tone(262, 0.5, 0.45, 'tri', decay=3.0))
    # 12 s loopable synth loop: 4 bars of bass + arpeggio at 120 bpm
    notes = [220.0, 220.0, 174.6, 196.0]            # A3 A3 F3 G3 (bass roots)
    arp = [1.0, 1.5, 2.0, 1.5]
    beat = 0.5
    song = []
    for bar in range(8):
        root = notes[bar % 4]
        for step in range(8):
            f = root * arp[step % 4] * 2
            song += _tone(f, beat / 2, 0.16, 'square', decay=3.5)
        # bass under arpeggio (mix later)
    bass = []
    for bar in range(8):
        root = notes[bar % 4] / 2
        for b in range(4):
            bass += _tone(root, beat, 0.30, 'tri', decay=2.0)
    n = min(len(song), len(bass))
    mix = [song[i] + bass[i] for i in range(n)]
    # fade ends to zero so the loop is click-free
    f = 200
    for i in range(f):
        mix[i] *= i / f
        mix[n - 1 - i] *= i / f
    _write_wav('music.wav', mix)


def _png(path, w, h, pixel):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw += bytes(pixel(x / (w - 1), y / (h - 1)))
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + \
        chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as fh:
        fh.write(png)


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


R_PATH = [(0.34, 0.20, 0.34, 0.80), (0.34, 0.80, 0.54, 0.80), (0.54, 0.80, 0.65, 0.73),
          (0.65, 0.73, 0.68, 0.64), (0.68, 0.64, 0.65, 0.55), (0.65, 0.55, 0.54, 0.49),
          (0.54, 0.49, 0.34, 0.49), (0.52, 0.49, 0.70, 0.20)]


def make_icon():
    os.makedirs(ICO, exist_ok=True)

    def pixel(u, v):
        v = 1.0 - v
        d = math.hypot(u - 0.5, v - 0.45)
        bg = (int(12 + 55 * d), int(14 + 10 * d), int(48 + 80 * (1 - d)))
        best = min(_seg_dist(u, v, *s) for s in R_PATH)
        if best < 0.055:
            return (255, 205, 40, 255)
        if best < 0.085:
            k = (0.085 - best) / 0.03
            return (int(bg[0] + (40 - bg[0]) * k), int(bg[1] + (200 - bg[1]) * k),
                    int(bg[2] + (255 - bg[2]) * k), 255)
        return (bg[0], bg[1], bg[2], 255)

    _png(os.path.join(ICO, 'icon.png'), 256, 256, pixel)


if __name__ == '__main__':
    make_sounds()
    make_icon()
    print('assets generated in', os.path.join(HERE, 'assets'))
