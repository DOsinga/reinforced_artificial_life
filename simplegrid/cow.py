import colorsys
import math
import random
from enum import IntEnum

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


MAX_ENERGY = 1000


class Action(IntEnum):
    NONE = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    SPLIT = 5

    def __repr__(self):
        return self.name

    def direction(self):
        dx = 0
        dy = 0
        if self == Action.UP:
            dy = -1
        elif self == Action.DOWN:
            dy = 1
        elif self == Action.LEFT:
            dx = -1
        elif self == Action.RIGHT:
            dx = 1
        return dx, dy


def random_color():
    hue = random.uniform(0.5, 1.1)
    lightness = random.uniform(0.5, 0.8)
    saturation = random.uniform(0.7, 0.9)
    return tuple(map(lambda f: int(f * 255), colorsys.hls_to_rgb(hue, lightness, saturation)))


class SimpleCow(object):
    id_count = 0

    def __init__(self, x, y, energy, color=None):
        self.x = x
        self.y = y
        self.color = color if color else random_color()
        self.actioncolor = BLACK
        self.energy = energy
        self.id = SimpleCow.id_count
        SimpleCow.id_count += 1

    def step(self):
        if self.energy > MAX_ENERGY:
            self.actioncolor = YELLOW
            return Action.SPLIT

        return random.choice(list(Action)[1:-1])

    def learn(self, state, reward, done):
        pass

    def draw(self, display):
        display.circle(
            self.color, self.x, self.y, 3 * min(1, math.sqrt(2 * self.energy / MAX_ENERGY))
        )
        display.circle(
            self.actioncolor, self.x, self.y, 1 * min(1, math.sqrt(2 * self.energy / MAX_ENERGY))
        )

    def split(self):
        new_creature = self.__class__(self.x, self.y, self.energy / 2, color=self.color)
        self.energy /= 2
        return new_creature

    def __repr__(self):
        return '\%s:%02d/' % (self.__class__.__name__, self.id)


class GreedyCow(SimpleCow):
    def action(self, nearby):
        neighbours = {
            (self.x - 1, self.y): Action.LEFT,
            (self.x + 1, self.y): Action.RIGHT,
            (self.x, self.y - 1): Action.UP,
            (self.x, self.y + 1): Action.DOWN,
        }

        possible_actions = [
            neighbours[(x, y)] for cell, x, y in nearby if (x, y) in neighbours.keys()
        ]
        if possible_actions:
            return random.choice(possible_actions)
        else:
            return super().action(nearby)
