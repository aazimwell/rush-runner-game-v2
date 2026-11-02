"""Local JSON persistence (fully offline). No Kivy imports."""
import json
import os

DEFAULTS = {
    'coins': 0, 'diamonds': 0, 'high_score': 0, 'best_distance': 0,
    'selected': 'robo', 'unlocked': ['robo'], 'level': 1, 'total_coins': 0,
    'music': True, 'sfx': True, 'quality': 'High', 'control': 'both',
    'sensitivity': 'Medium', 'language': 'English', 'tilt_offset': 0.0,
}


class SaveManager:
    def __init__(self, path):
        self.path = path
        self.data = dict(DEFAULTS)
        self.data['unlocked'] = list(DEFAULTS['unlocked'])

    def load(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                for k, default in DEFAULTS.items():
                    v = raw.get(k, default)
                    if isinstance(default, bool):
                        ok = isinstance(v, bool)
                    elif isinstance(default, (int, float)):
                        ok = isinstance(v, (int, float)) and not isinstance(v, bool)
                    else:
                        ok = isinstance(v, type(default))
                    self.data[k] = v if ok else default
                if 'robo' not in self.data['unlocked']:
                    self.data['unlocked'].append('robo')
        except (OSError, ValueError):
            pass  # first run or corrupt file -> defaults
        return self

    def save(self):
        try:
            folder = os.path.dirname(self.path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            tmp = self.path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self.data, f)
            os.replace(tmp, self.path)
            return True
        except OSError:
            return False

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v
