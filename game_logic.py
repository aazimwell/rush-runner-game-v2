"""Pure game rules: lanes, spawning, collisions, scoring. No Kivy imports.

Units: 1 lane width = 1.0 horizontal unit, depth in metres. The player sits at
depth 0; objects have an absolute position 'at' and are ahead while at > dist.
"""
import random

FAR = 80.0            # spawn horizon (m)
GRAV = 19.0
JUMP_V = 7.4
SLIDE_TIME = 0.75
LOW_CLEAR = 0.62      # must be this high to pass a 'low' barrier
HIGH_CLEAR = 0.25     # must be below this (and sliding) to pass a 'high' beam


class World:
    def __init__(self, char, level=1, seed=None):
        self.rng = random.Random(seed)
        self.char = char
        self.level = level
        self.max_hp = char['health']
        self.hp = self.max_hp
        self.lane = 0
        self.x = 0.0
        self.jy = 0.0
        self.vy = 0.0
        self.slide_t = 0.0
        self.invuln = 0.0
        self.dist = 0.0
        self.speed = 0.0
        self.phase = 0.0
        self.t = 0.0
        self.score_f = 0.0
        self.coins = 0
        self.diamonds = 0
        self.objs = []
        self.next_at = 38.0
        self.target = 500.0 + 300.0 * level
        self.state = 'run'     # run | dead | complete
        self.events = []
        self._spawn()

    # ---- player actions -------------------------------------------------
    def move(self, d):
        if self.state != 'run':
            return False
        new = max(-1, min(1, self.lane + d))
        if new == self.lane:
            return False
        self.lane = new
        self.events.append('lane')
        return True

    def jump(self):
        if self.state == 'run' and self.jy <= 0.001 and self.slide_t <= 0:
            self.vy = JUMP_V
            self.jy = 0.002
            self.events.append('jump')
            return True
        return False

    def slide(self):
        if self.state != 'run':
            return False
        if self.jy > 0.001:
            self.vy = -15.0           # fast-fall into the slide
        self.slide_t = SLIDE_TIME
        self.events.append('slide')
        return True

    # ---- derived values -------------------------------------------------
    @property
    def multiplier(self):
        return min(5, 1 + self.coins // 25)

    @property
    def score(self):
        return int(self.score_f)

    @property
    def sliding(self):
        return self.slide_t > 0 and self.jy <= 0.05

    def stars(self):
        s = 1
        if self.coins >= 20 * self.level:
            s += 1
        if self.hp == self.max_hp:
            s += 1
        return s

    # ---- spawning -------------------------------------------------------
    def _coin_line(self, lane, start, n):
        for i in range(n):
            self.objs.append({'kind': 'coin', 'lane': lane, 'at': start + i * 2.3, 'taken': False})

    def _spawn(self):
        while self.next_at - self.dist < FAR:
            at = self.next_at
            r = self.rng.random()
            lanes = [-1, 0, 1]
            if r < 0.30:
                self._coin_line(self.rng.choice(lanes), at, self.rng.randint(6, 10))
            elif r < 0.92:
                k = self.rng.choice([1, 1, 2])
                blocked = self.rng.sample(lanes, k)
                free = [l for l in lanes if l not in blocked]
                for l in blocked:
                    kind = self.rng.choices(['low', 'high', 'block'], [0.40, 0.30, 0.30])[0]
                    self.objs.append({'kind': kind, 'lane': l, 'at': at + 8.0, 'taken': False})
                if free and self.rng.random() < 0.7:
                    self._coin_line(self.rng.choice(free), at, 6)
                if free and self.rng.random() < 0.08:
                    self.objs.append({'kind': 'diamond', 'lane': self.rng.choice(free),
                                      'at': at + 3.0, 'taken': False})
            else:
                self.objs.append({'kind': 'diamond', 'lane': self.rng.choice(lanes),
                                  'at': at, 'taken': False})
                self._coin_line(self.rng.choice(lanes), at + 6.0, 5)
            self.next_at += self.rng.uniform(22.0, 30.0) - min(4.0, self.dist / 600.0)

    # ---- simulation -----------------------------------------------------
    def update(self, dt):
        if self.state != 'run':
            return
        self.t += dt
        base = 15.0 + (self.level - 1) * 1.5
        self.speed = min(base + self.dist * 0.010, 38.0) * self.char['speed']
        self.dist += self.speed * dt
        self.x += (self.lane - self.x) * min(1.0, dt * 13.0)
        if abs(self.lane - self.x) < 0.005:
            self.x = float(self.lane)
        if self.jy > 0 or self.vy > 0:
            self.vy -= GRAV * dt
            self.jy += self.vy * dt
            if self.jy <= 0:
                self.jy = 0.0
                self.vy = 0.0
        if self.slide_t > 0:
            self.slide_t -= dt
        if self.invuln > 0:
            self.invuln -= dt
        self.phase += dt * self.speed * 0.55
        self.score_f += self.speed * dt * self.multiplier
        self._spawn()
        self._collide(dt)
        self.objs = [o for o in self.objs if o['at'] - self.dist > -5.0]
        if self.hp <= 0:
            self.state = 'dead'
        elif self.dist >= self.target:
            self.state = 'complete'

    def _collide(self, dt):
        hw = max(0.7, self.speed * dt)
        mag = self.char['magnet']
        for o in self.objs:
            if o['taken']:
                continue
            dz = o['at'] - self.dist
            if dz > hw + 4.0 or dz < -hw:
                continue
            dl = abs(o['lane'] - self.x)
            k = o['kind']
            if k in ('coin', 'diamond'):
                if abs(dz) < hw + (mag - 1.0) * 3.0 and dl < 0.55 + (mag - 1.0) * 0.9:
                    o['taken'] = True
                    if k == 'coin':
                        self.coins += 1
                        self.score_f += 10 * self.multiplier
                        self.events.append('coin')
                    else:
                        self.diamonds += 1
                        self.score_f += 50 * self.multiplier
                        self.events.append('diamond')
                continue
            if abs(dz) >= hw or dl >= 0.6:
                continue
            if k == 'low':
                hit = self.jy < LOW_CLEAR
            elif k == 'high':
                hit = not (self.sliding and self.jy < HIGH_CLEAR)
            else:
                hit = True
            if hit and self.invuln <= 0:
                o['taken'] = True
                self.hp -= 1
                self.invuln = self.char['invuln']
                self.events.append('hit')

    def pop_events(self):
        e, self.events = self.events, []
        return e

    def result(self):
        return {'score': self.score, 'coins': self.coins, 'diamonds': self.diamonds,
                'distance': int(self.dist), 'stars': self.stars(),
                'won': self.state == 'complete', 'level': self.level}
