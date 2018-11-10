#!/usr/bin/env python
import numpy as np
import random

from simplegrid.cow import SimpleCow, Action

MIN_ENERGY = 5
INIT_ENERGY = 500
GRASS_ENERGY = 25
IDLE_COST = 1
MOVE_COST = 2

class World:
    ZOOM = 4
    def __init__(self, size, grass_fraction=0.1):
        self.creatures = {}
        self.size = size
        self.cells = np.zeros((size, size))
        c = size * size
        for i in np.random.choice(c, int(grass_fraction * c)):
            self.cells[i // size, i % size] = -1

        for _ in range(10):
            x, y = self.free_spot()
            creature = SimpleCow(x, y, INIT_ENERGY)
            self.creatures[creature.id] = creature
            self.cells[x, y] = creature.id

    def free_spot(self):
        while True:
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if self.cells[x, y] == 0:
                return x, y

    def step(self):
        dead = set()
        born = []
        for creature in self.creatures.values():
            if creature.id in dead:
                continue

            action = creature.step()
            new_creature, state, reward, done, _ = self.process_action(creature, action)
            creature.learn(state, reward, done)

            if done:
                dead.add(creature)
            if new_creature:
                born.append(new_creature)

        for creature in dead:
            self.cells[creature.x, creature.y] = 0
            del self.creatures[creature.id]

        for creature in born:
            self.creatures[creature.id] = creature
            self.cells[creature.x, creature.y] = creature.id

        # Watching grass grow
        for _ in range(3):
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if self.cells[x, y] == 0:
                self.cells[x, y] = -1

    def draw(self, display):
        for x in range(self.size):
            for y in range(self.size):
                idx = self.cells[x, y]
                if idx < 0:
                    color = (100, 240, 100)
                    display.circle(color, x, y, 1)
                elif idx > 0:
                    self.creatures[idx].draw(display)

    def get_info(self):
        return str(len(self.creatures))

    def apply_direction(self, option, x, y):
        dx, dy = option.direction()
        x = (x + dx) % self.size
        y = (y + dy) % self.size
        return x, y

    def process_action(self, creature, action):
        new_creature = None
        reward = 0
        if action == Action.NONE:
            creature.energy -= IDLE_COST
        elif action == Action.SPLIT:
            options = list(Action)
            random.shuffle(options)
            for option in options:
                x, y = self.apply_direction(option, creature.x, creature.y)
                if self.cells[x, y] == 0:
                    new_creature = creature.split()
                    reward = 10
                    break
        else:
            self.cells[creature.x, creature.y] = 0
            x, y = self.apply_direction(action, creature.x, creature.y)
            if self.cells[x, y] <= 0:
                if self.cells[x, y] == -1:
                    reward = 1
                    creature.energy += GRASS_ENERGY
                creature.x = x
                creature.y = y
            self.cells[creature.x, creature.y] = creature.id
            creature.energy -= MOVE_COST

        done = creature.energy < MIN_ENERGY

        size_2 = self.size // 2

        rolled = np.roll(self.cells, (size_2 - creature.x, size_2 - creature.y), (0, 1))
        observation = rolled[size_2 - 1 : size_2 + 2, size_2 - 1 : size_2 + 2]

        return new_creature, observation, reward, done, {}

