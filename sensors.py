"""Real accelerometer access on Android via plyer (-> android.hardware.SensorManager).

Nothing here is simulated: on a device without the sensor (or on desktop) the
sensor reports available=False and tilt control simply stays idle.
"""


class AccelSensor:
    def __init__(self):
        self.available = False
        self.enabled = False
        self.reason = 'not started'
        self._acc = None

    def start(self):
        if self.enabled:
            return self.available
        try:
            from plyer import accelerometer
            accelerometer.enable()
            self._acc = accelerometer
            self.enabled = True
            self.available = True
            self.reason = 'ok'
        except Exception as e:  # NotImplementedError on desktop, jnius errors, ...
            self._acc = None
            self.enabled = False
            self.available = False
            self.reason = '%s: %s' % (type(e).__name__, e)
        return self.available

    def stop(self):
        if self._acc is not None:
            try:
                self._acc.disable()
            except Exception:
                pass
        self.enabled = False

    def read(self):
        """Return (x, y, z) in m/s^2 or None when no valid reading yet."""
        if not self.enabled or self._acc is None:
            return None
        try:
            v = self._acc.acceleration
        except Exception:
            return None
        if not v or v[0] is None:
            return None
        return v


def exclude_system_gestures():
    """Best effort (Android 10+): ask the system not to treat edge swipes as Back/Home
    gestures while the game is on screen. Silently does nothing elsewhere."""
    try:
        from android.runnable import run_on_ui_thread
        from jnius import autoclass

        @run_on_ui_thread
        def _apply():
            try:
                Build = autoclass('android.os.Build$VERSION')
                if Build.SDK_INT < 29:
                    return
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Rect = autoclass('android.graphics.Rect')
                ArrayList = autoclass('java.util.ArrayList')
                view = PythonActivity.mActivity.getWindow().getDecorView()
                rects = ArrayList()
                rects.add(Rect(0, 0, view.getWidth(), view.getHeight()))
                view.setSystemGestureExclusionRects(rects)
            except Exception:
                pass

        _apply()
    except Exception:
        pass
