import math
import random
from enum import Enum

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


MIN_ENERGY = 5
MAX_ENERGY = 50

class Action(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    SPLIT = 4

    def __repr__(self):
        return self.name


class Cow(object):
    id_count = 0

    def __init__(self, x, y, color, energy):
        self.x = x
        self.y = y
        self.color = color
        self.actioncolor = BLACK
        self.energy = energy
        self.id = Cow.id_count
        Cow.id_count += 1

    def __str__(self):
        return f'COW {self.id}, ({self.x},{self.y}) - {self.energy}'

    def step(self, nearby):
        if self.energy > MAX_ENERGY:
            self.actioncolor = YELLOW
            return Action.SPLIT

        return self.action( nearby )

    def action(self, nearby):
        return random.choice(list(Action)[:4])

    def draw(self, display):
        display.circle(self.color, self.x, self.y, 1 * min(1,math.sqrt(2*self.energy/MAX_ENERGY)))
        display.circle(self.actioncolor, self.x, self.y, .3 * min(1,math.sqrt(2*self.energy/MAX_ENERGY)))

    def radius(self):
        return math.sqrt(self.energy)

    def split(self):
        new_creature = Cow(self.x, self.y, self.color, self.energy / 2)
        self.energy /= 2
        return new_creature

    def __repr__(self):
        return '\%02d/' % self.id


class GreedyCow( Cow ):

    def action(self, nearby):
        neighbours = {(self.x-1, self.y): Action.LEFT,
                      (self.x+1, self.y): Action.RIGHT,
                      (self.x, self.y-1): Action.UP,
                      (self.x, self.y+1): Action.DOWN}

        possible_actions = [neighbours[(x,y)] for cell, x, y in nearby if (x,y) in neighbours.keys()]
        if possible_actions:
            return random.choice(possible_actions)
        else:
            return random.choice(list(Action)[:4])
