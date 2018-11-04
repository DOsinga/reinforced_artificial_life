#!/usr/bin/env python

import numpy as np
import random

class World:
    def __init__(self, size, grass_fraction):
        self.cow_x = size // 2
        self.cow_y = size // 2
        self.cow_energy = 100
        self.size = size
        self.cells = np.zeros((size, size))
        c = size * size
        for i in np.random.choice(c, int(grass_fraction * c)):
            self.cells[i // size, i % size] = -1

    def step(self):
        self.move(random.randrange(4))
        x = random.randrange(self.size)
        y = random.randrange(self.size)
        if self.cells[x, y] == 0:
            self.cells[x, y] = -1

    def draw(self, display):
        radius = 10
        size_2  = self.size / 2
        for x in range(self.size):
            for y in range(self.size):
                if x == self.cow_x and y == self.cow_y:
                    color = (255, 100, 100)
                elif self.cells[x, y] < 0:
                    color = (100, 255, 100)
                else:
                    continue
                display.circle(color, (x - size_2) * radius, (y - size_2) * radius, radius / 2)

    def get_info(self):
        return str(self.cow_energy)

    def move(self, direction):
        """
        Args:
            direction: direction to move in (0, 3)

        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """

        dx, dy = [(-1, 0), (0, 1), (1, 0), (0, -1)][direction]
        next_x = (self.cow_x + dx + self.size) % self.size
        next_y = (self.cow_y + dy + self.size) % self.size
        reward = 0
        if self.cells[next_x, next_y] < 0:
            reward = 1
            self.cow_energy += 5
        else:
            self.cow_energy -= 1

        self.cells[self.cow_x, self.cow_y] = 0

        self.cow_x = next_x
        self.cow_y = next_y

        self.cells[self.cow_x, self.cow_y] = 1

        done = self.cow_energy <= 0

        size_2 = self.size // 2

        rolled = np.roll(self.cells, (size_2 - next_x, size_2 - next_y), (0, 1))
        observation = rolled[size_2 - 1: size_2 + 2, size_2 - 1: size_2 + 2]

        return observation, reward, done, {}