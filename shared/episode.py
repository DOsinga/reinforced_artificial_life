import json
import numpy as np


class Episode:
    def __init__(self):
        self.frames = []  # This is the episode, a list of frames
        self.cur_grid = []  # Internal param to keep track of the current frame grid
        self.cur_creatures = []  # Internal param to keep track of the current frame creatures

    def creature_change(self, creature_id, energy, creature_type=None):
        creature = {'id': creature_id, 'energy': energy}
        if creature_type:
            creature['creature_type'] = creature_type
        self.cur_creatures += [creature]

    def grid_change(self, x, y, value):
        self.cur_grid += [{'x': x, 'y': y, 'value': value}]

    def next_frame(self):
        self.frames += [{'creatures': self.cur_creatures, 'grid': self.cur_grid}]
        self.cur_creatures = []
        self.cur_grid = []

    def load(self):
        pass

    def save(self, settings):
        path = settings.get_path('episodes.jsonl')
        if path:
            with open(path, 'w') as f:
                f.write(
                    '\n'.join(
                        [json.dumps(frame, default=fallback_to_int) for frame in self.frames]
                    )
                )


def fallback_to_int(o):
    """json.dumps cannot handle np.int64 data so this helper function is to convert it to int"""
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError
