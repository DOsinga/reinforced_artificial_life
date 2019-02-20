from enum import Enum
import numpy as np


class MapFeature(Enum):
    # CREATURE is a place holder:
    CREATURE = 1, '@', (240, 20, 20)
    EMPTY = 0, '.', (0, 0, 0)
    ROCK = -2, '*', (128, 128, 128)
    WATER = -3, '~', (0, 0, 255)

    def __new__(cls, value, char, color):
        """Yes, this is the official way to overload an Enum."""
        obj = object.__new__(cls)
        obj._value_ = value
        obj.index = value
        obj.char = char
        obj.color = color
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        cls.registry[obj.char] = obj
        return obj

    @classmethod
    def from_char(cls, char):
        return cls.registry[char]

    @classmethod
    def text_scene_to_environment(cls, text_scene):
        text_scene = text_scene.strip()
        return np.asarray(
            [[cls.from_char(char).index for char in line] for line in text_scene.split('\n')]
        ).T

    def to_feature_vector(self, vector):
        """Convert the vector to a feature vector.

        Returns:
            A copy of vector where each entry is 1 if it matches self.index or 0 if not.
        """
        if self == MapFeature.CREATURE:
            raise ValueError('to_feature does not work for CREATURE')
        res = np.copy(vector).flatten()
        res[res != self.index] = 0
        res[res == self.index] = 1

        return res
