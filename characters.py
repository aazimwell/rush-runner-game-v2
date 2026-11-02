"""Playable characters. Their look is drawn in player.py (no image files needed)."""

CHARACTERS = [
    dict(id='robo', name='Robo Runner', desc='A young hero with\nunlimited energy!',
         health=3, speed=1.00, magnet=1.0, invuln=1.5, cost=0,
         ability='Balanced all-rounder'),
    dict(id='female', name='Female Runner', desc='Quick, graceful and\nalways chasing coins.',
         health=3, speed=1.10, magnet=1.4, invuln=1.5, cost=500,
         ability='Coin Charm: wide magnet'),
    dict(id='shadow', name='Shadow Runner', desc='A silent ghost of\nthe rooftops.',
         health=2, speed=1.20, magnet=1.0, invuln=2.8, cost=1500,
         ability='Shadow Step: 2.8s safety'),
    dict(id='panda', name='Panda Runner', desc='Slow, tough and\nvery lovable.',
         health=5, speed=0.92, magnet=1.7, invuln=1.5, cost=3000,
         ability='Bamboo Armor: 5 hearts'),
]

BY_ID = {c['id']: c for c in CHARACTERS}
MAX_HEALTH, MAX_SPEED, MAX_MAGNET = 5.0, 1.25, 1.8


def get(cid):
    return BY_ID.get(cid, CHARACTERS[0])
