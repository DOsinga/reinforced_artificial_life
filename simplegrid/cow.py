import math
import random
from enum import IntEnum
import operator
import abc

from simplegrid.map_feature import MapFeature

MAX_ENERGY = 1000


class Action(IntEnum):
    GRAZE = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    SPLIT = 5

    @classmethod
    def from_letter(cls, letter):
        number = 'URDL'.find(letter) + 1
        return cls(number)

    def __repr__(self):
        return self.name

    def to_direction(self):
        return {Action.UP: (0, -1), Action.RIGHT: (1, 0), Action.DOWN: (0, 1), Action.LEFT: (-1, 0)}[self]

    def to_observation(self, offset):
        direction = self.to_direction()
        return direction[0] + offset, direction[1] + offset


class AbstractCow(abc.ABC):
    id_count = 1

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'COLOR'):
            raise TypeError('Cows need to declare their color')

    def __init__(self, x, y, settings, energy=None):
        self.x = x
        self.y = y
        self.settings = settings
        self.energy = energy or settings.init_energy
        self.id = AbstractCow.id_count
        AbstractCow.id_count += 1

    @abc.abstractmethod
    def step(self, observation):
        pass

    def learn(self, reward, done):
        pass

    def draw(self, display):
        display.circle(self.x, self.y, math.sqrt(min(0.64, 2 * self.energy / MAX_ENERGY)), self.__class__.COLOR)

    def split(self):
        new_creature = self.__class__(self.x, self.y, self.settings, self.energy / 2)
        self.energy /= 2
        return new_creature

    def __repr__(self):
        return '\%s:%02d/' % (self.__class__.__name__, self.id)


class SimpleCow(AbstractCow):

    COLOR = (120, 240, 20)

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        return random.choice(list(Action)[1:-1])


class GreedyCow(AbstractCow):

    COLOR = (240, 20, 20)

    def step(self, observation):

        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        offset = observation.shape[0] // 2
        possible_actions = list(Action)[1:-1]
        interesting_actions = [a for a in possible_actions if observation[a.to_observation(offset)] == -1]

        if interesting_actions:
            return random.choice(interesting_actions)
        else:
            return Action.RIGHT  # Was: random.choice(possible_actions)


class SmartCow(SimpleCow):

    COLOR = (240, 120, 20)

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        size = observation.shape[0]
        view_distance = size // 2

        # Initial value of a is to favor one direction a little more than others
        # The random is to prevent creature from ending up in an oscillator
        possible_actions = {a: (a + 2 * random.random()) / 100 for a in list(Action)[:-1]}

        for col in range(size):
            x = col - view_distance
            for row in range(size):
                reward = observation[col, row, 0]
                y = row - view_distance
                dist = abs(x) + abs(y)
                if dist == 0:
                    possible_actions[Action.GRAZE] += reward * 5
                elif dist <= view_distance:
                    value = observation[col, row, 1]
                    if dist == 1 and value == MapFeature.ROCK.index:
                        reward += -1
                    elif dist == 1 and value == MapFeature.WATER.index:
                        reward -= self.energy / self.settings.grass_energy
                    elif value == MapFeature.CREATURE.index:
                        reward -= 0.5
                    else:
                        continue
                    reward /= dist * dist
                    if x < 0:
                        possible_actions[Action.LEFT] += reward
                    elif x > 0:
                        possible_actions[Action.RIGHT] += reward
                    if y < 0:
                        possible_actions[Action.UP] += reward
                    elif y > 0:
                        possible_actions[Action.DOWN] += reward
        best_action = max(possible_actions.items(), key=operator.itemgetter(1))[0]
        return best_action
