import abc
import math
from enum import IntEnum

MAX_ENERGY = 1000


class Action(IntEnum):
    NONE = 0
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


class AbstractCreature(abc.ABC):
    id_count = 1

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'COLOR'):
            raise TypeError('Creatures need to declare their color')

    def __init__(self, x, y, settings, energy=None):
        self.x = x
        self.y = y
        self.settings = settings
        self.energy = energy or settings.init_energy
        self.id = AbstractCreature.id_count
        AbstractCreature.id_count += 1

    @staticmethod
    def is_predator():
        return False

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
