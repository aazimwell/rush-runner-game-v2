"""Headless unit tests for everything that does not need Kivy or a phone.
Run:  python -m unittest -v test_logic
"""
import json
import os
import tempfile
import unittest

import characters
import controls
import game_logic as gl
import save_manager
import settings


def world(cid='robo', level=1, seed=3):
    return gl.World(characters.get(cid), level, seed)


class WorldTests(unittest.TestCase):
    def test_lane_moves_clamped(self):
        w = world()
        self.assertTrue(w.move(-1))
        self.assertFalse(w.move(-1))          # already at left edge
        self.assertTrue(w.move(1))
        self.assertTrue(w.move(1))
        self.assertFalse(w.move(1))
        for _ in range(60):
            w.update(1 / 60)
        self.assertAlmostEqual(w.x, w.lane, places=2)

    def test_jump_and_slide(self):
        w = world()
        self.assertTrue(w.jump())
        self.assertFalse(w.jump())            # no double jump
        peak = 0
        for _ in range(120):
            w.update(1 / 60)
            peak = max(peak, w.jy)
        self.assertGreater(peak, 1.0)
        self.assertEqual(w.jy, 0.0)
        w.slide()
        self.assertTrue(w.sliding)

    def test_speed_and_distance_increase(self):
        w = world()
        s0 = None
        for i in range(600):
            w.update(1 / 60)
            if i == 1:
                s0 = w.speed
        self.assertGreater(w.dist, 100)
        self.assertGreater(w.speed, s0)
        self.assertGreater(w.score, 0)

    def _single(self, kind, lane=0, **pre):
        w = world()
        w.objs = [{'kind': kind, 'lane': lane, 'at': 12.0, 'taken': False}]
        w.next_at = 1e9
        for k, v in pre.items():
            setattr(w, k, v)
        return w

    def _run(self, w, secs=2.0, actions=None):
        for i in range(int(secs * 60)):
            if actions:
                actions(w, i)
            w.update(1 / 60)

    def test_coin_collected_only_in_own_lane(self):
        w = self._single('coin', 0)
        self._run(w)
        self.assertEqual(w.coins, 1)
        w = self._single('coin', 1)
        self._run(w)
        self.assertEqual(w.coins, 0)

    def test_block_hits_and_lane_change_avoids(self):
        w = self._single('block', 0)
        self._run(w)
        self.assertEqual(w.hp, w.max_hp - 1)
        w = self._single('block', 0)
        w.move(1)
        self._run(w)
        self.assertEqual(w.hp, w.max_hp)

    def test_low_barrier_needs_jump(self):
        w = self._single('low', 0)
        self._run(w)
        self.assertEqual(w.hp, w.max_hp - 1)
        w = self._single('low', 0)
        # time the jump so that the apex is over the barrier
        def act(wd, i):
            if abs(wd.dist - 7.0) < 0.5 and wd.jy == 0:
                wd.jump()
        self._run(w, actions=act)
        self.assertEqual(w.hp, w.max_hp)

    def test_high_beam_needs_slide(self):
        w = self._single('high', 0)
        self._run(w)
        self.assertEqual(w.hp, w.max_hp - 1)
        w = self._single('high', 0)
        def act(wd, i):
            if wd.dist > 9.5 and wd.slide_t <= 0 and wd.dist < 11:
                wd.slide()
        self._run(w, actions=act)
        self.assertEqual(w.hp, w.max_hp)

    def test_game_over_when_hp_zero_and_invulnerability(self):
        w = world('shadow')                   # 2 hearts
        for i in range(2):
            w.objs = [{'kind': 'block', 'lane': 0, 'at': w.dist + 2.0, 'taken': False}]
            w.next_at = 1e9
            self._run(w, 1.0)
            w.invuln = 0
        self.assertEqual(w.state, 'dead')
        self.assertEqual(w.hp, 0)

    def test_level_complete(self):
        w = world()
        w.dist = w.target - 1
        w.next_at = 1e9
        w.objs = []
        self._run(w, 1.0)
        self.assertEqual(w.state, 'complete')
        r = w.result()
        self.assertTrue(r['won'])
        self.assertIn(r['stars'], (1, 2, 3))

    def test_spawner_never_blocks_all_lanes_with_blocks(self):
        w = world(seed=11)
        for _ in range(3000):
            w.update(1 / 60)
            w.hp = w.max_hp
            w.state = 'run'
            w.dist = min(w.dist, 1e5)
        rows = {}
        for o in w.objs:
            if o['kind'] == 'block':
                rows.setdefault(round(o['at'], 1), set()).add(o['lane'])
        for lanes in rows.values():
            self.assertLess(len(lanes), 3)


class ControlTests(unittest.TestCase):
    def test_swipe_directions_single_fire(self):
        d = controls.SwipeDetector(0.07)
        d.start(500, 500)
        self.assertIsNone(d.move(510, 505, 1000))
        self.assertEqual(d.move(600, 510, 1000), 'right')
        self.assertIsNone(d.move(900, 510, 1000))        # no repeat in same stroke
        d.start(500, 500)
        self.assertEqual(d.move(400, 495, 1000), 'left')
        d.start(500, 500)
        self.assertEqual(d.move(505, 620, 1000), 'up')   # kivy y grows upward
        d.start(500, 500)
        self.assertEqual(d.move(495, 380, 1000), 'down')

    def test_tilt_dead_zone_and_single_move(self):
        t = controls.TiltController(thresh=2.0, dead=0.9)
        now = 0.0
        out = []
        for _ in range(30):                              # neutral, jitter inside dead zone
            now += 0.02
            out.append(t.feed(0.3, now))
        self.assertEqual([o for o in out if o], [])
        out = []
        for _ in range(60):                              # tilt right (android x negative)
            now += 0.02
            out.append(t.feed(-4.0, now))
        self.assertEqual([o for o in out if o], ['right'])  # exactly one lane move
        out = []
        for _ in range(60):                              # back to neutral -> no move
            now += 0.02
            out.append(t.feed(0.0, now))
        self.assertEqual([o for o in out if o], [])
        for _ in range(60):                              # tilt left -> one move
            now += 0.02
            out.append(t.feed(4.0, now))
        self.assertEqual([o for o in out if o], ['left'])

    def test_tilt_calibration_shifts_neutral(self):
        t = controls.TiltController(thresh=2.0, dead=0.9)
        now = 0.0
        for _ in range(40):                              # phone held at an angle
            now += 0.02
            t.feed(-3.0, now)
        self.assertTrue(t.calibrate())
        out = []
        for _ in range(60):
            now += 0.02
            out.append(t.feed(-3.0, now))
        self.assertEqual([o for o in out if o], [])      # held pose is now neutral
        self.assertAlmostEqual(t.value, 0.0, places=1)
        self.assertFalse(controls.TiltController().calibrate())  # no data -> False


class SaveTests(unittest.TestCase):
    def test_roundtrip_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'sub', 'save.json')
            s = save_manager.SaveManager(p).load()
            self.assertEqual(s['coins'], 0)
            s['coins'] = 123
            s['high_score'] = 4567
            s['music'] = False
            s['selected'] = 'panda'
            self.assertTrue(s.save())
            s2 = save_manager.SaveManager(p).load()
            self.assertEqual((s2['coins'], s2['high_score'], s2['music'], s2['selected']),
                             (123, 4567, False, 'panda'))
            with open(p, 'w') as f:
                f.write('{not json')
            self.assertEqual(save_manager.SaveManager(p).load()['coins'], 0)
            with open(p, 'w') as f:
                json.dump({'coins': 'oops', 'music': 5}, f)
            s3 = save_manager.SaveManager(p).load()
            self.assertEqual((s3['coins'], s3['music']), (0, True))

    def test_settings_cycle_and_strings(self):
        s = save_manager.SaveManager(os.path.join(tempfile.mkdtemp(), 's.json')).load()
        self.assertEqual(settings.cycle(s, 'control', 1), 'touch')
        self.assertEqual(settings.cycle(s, 'quality', -1), 'Medium')
        for lang in settings.OPTIONS['language']:
            for k in settings.STR['English']:
                self.assertTrue(settings.tr(lang, k))
        self.assertEqual(set(settings.STR['English']), set(settings.STR['Español']))
        self.assertEqual(set(settings.STR['English']), set(settings.STR['Français']))


if __name__ == '__main__':
    unittest.main()
