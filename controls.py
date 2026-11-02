"""Swipe and tilt interpretation. Pure Python (no Kivy) so it can be unit-tested."""


class SwipeDetector:
    """One detector per finger. Fires at most ONE gesture per stroke, the moment the
    finger has moved far enough (no waiting for finger-up -> no input lag)."""

    def __init__(self, min_frac=0.07):
        self.min_frac = min_frac
        self.sx = self.sy = 0.0
        self.fired = False

    def start(self, x, y):
        self.sx, self.sy = x, y
        self.fired = False

    def move(self, x, y, ref):
        """ref = reference length in px (screen width). Kivy y axis points up."""
        if self.fired:
            return None
        dx, dy = x - self.sx, y - self.sy
        if max(abs(dx), abs(dy)) < ref * self.min_frac:
            return None
        self.fired = True
        if abs(dx) >= abs(dy):
            return 'right' if dx > 0 else 'left'
        return 'up' if dy > 0 else 'down'


class TiltController:
    """Turns raw accelerometer x into discrete lane moves.

    Android reports x < 0 when the phone's right edge tilts down, so tilt = -x.
    Pipeline: low-pass smoothing -> subtract calibrated neutral -> dead zone ->
    threshold -> one lane per tilt (must return to neutral to move again).
    """

    def __init__(self, thresh=2.0, dead=0.9, offset=0.0, alpha=0.25, cooldown=0.22):
        self.thresh = thresh
        self.dead = dead
        self.offset = offset
        self.alpha = alpha
        self.cooldown = cooldown
        self.filtered = None
        self.armed = True
        self.last_t = -10.0

    def configure(self, thresh, dead):
        self.thresh, self.dead = thresh, dead

    def reset(self):
        self.filtered = None
        self.armed = False   # must see neutral before the first move

    @property
    def value(self):
        """Current calibrated tilt (positive = right). 0 if no data yet."""
        if self.filtered is None:
            return 0.0
        return self.filtered - self.offset

    def calibrate(self):
        """Take the current smoothed reading as neutral. False if no data."""
        if self.filtered is None:
            return False
        self.offset = self.filtered
        self.armed = False
        return True

    def feed(self, raw_x, t):
        tilt = -float(raw_x)
        if self.filtered is None:
            self.filtered = tilt
        else:
            self.filtered += (tilt - self.filtered) * self.alpha
        v = self.filtered - self.offset
        if abs(v) < self.dead:
            self.armed = True
            return None
        if self.armed and abs(v) >= self.thresh and t - self.last_t >= self.cooldown:
            self.armed = False
            self.last_t = t
            return 'right' if v > 0 else 'left'
        return None
