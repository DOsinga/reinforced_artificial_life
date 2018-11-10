#!/usr/bin/env python
import numpy as np
import random

from simplegrid.cow import SimpleCow, GreedyCow, Action

MIN_ENERGY = 5
INIT_ENERGY = 500
GRASS_ENERGY = 25
IDLE_COST = 1
MOVE_COST = 2
START_NUM_CREATURES=1

class World:
    def __init__(self, size, display, grass_fraction=0.5):
        display.scale = 4
        display.offset_x = display.scale * size / 2
        display.offset_y = display.scale * size / 2
        self.creatures = {}
        self.size = size
        self.cells = np.zeros((size, size))
        c = size * size
        for i in np.random.choice(c, int(grass_fraction * c)):
            self.cells[i // size, i % size] = -1

        for _ in range(START_NUM_CREATURES+1):
            x, y = self.free_spot()
            self.add_new_creature(GreedyCow(x, y, INIT_ENERGY))

    def free_spot(self):
        while True:
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if self.cells[x, y] == 0:
                return x, y

    def add_new_creature(self, creature):
        self.creatures[creature.id] = creature
        self.cells[creature.x, creature.y] = creature.id
        _, state, reward, done, _ = self.process_action(creature, Action.NONE)
        creature.learn(state, reward, done)

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
                    self.add_new_creature(new_creature)
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

