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
    id_count = 1

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
            self.x, self.y, min(0.8, math.sqrt(2 * self.energy / MAX_ENERGY)), self.color
        )
        display.circle(
            self.x,
            self.y,
            0.3 * min(0.8, math.sqrt(2 * self.energy / MAX_ENERGY)),
            self.actioncolor,
        )

    def split(self):
        new_creature = self.__class__(self.x, self.y, self.energy / 2, color=self.color)
        self.energy /= 2
        return new_creature

    def __repr__(self):
        return '\%s:%02d/' % (self.__class__.__name__, self.id)


class GreedyCow(SimpleCow):
    def learn(self, state, reward, done):
        self.state = state

    def step(self):

        if self.energy > MAX_ENERGY:
            self.actioncolor = YELLOW
            return Action.SPLIT

        neighbours = {
            (0, 1): Action.UP,
            (2, 1): Action.DOWN,
            (1, 2): Action.RIGHT,
            (1, 0): Action.LEFT,
        }

        possible_actions = []
        for dir, action in neighbours.items():
            if self.state[dir] == -1:
                possible_actions += [action]

        if possible_actions:
            return random.choice(possible_actions)
        else:
            return random.choice(list(Action)[1:-1])
