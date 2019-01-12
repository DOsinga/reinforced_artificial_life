#!/usr/bin/env python
from collections import Counter

import numpy as np
import random

from simplegrid.cow import SimpleCow, GreedyCow, Action, BLUE, RED, YELLOW
from simplegrid.deep_cow import DeepCow
from simplegrid.dqn_agent import DQNAgent

MIN_ENERGY = 5
INIT_ENERGY = 100
GRASS_ENERGY = 15
IDLE_COST = 1
MOVE_COST = 2
BATCH_SIZE = 32

START_NUM_CREATURES = 6
START_GRASS_FRACTION = 0.3


class World:
    def __init__(self, size, display):
        self.counts = {}
        display.offset_x = 0
        display.offset_y = 0
        self.creatures = {}
        self.size = size
        self.cells = np.zeros((size, size))

    def reset(self, episode, grass_fraction=START_GRASS_FRACTION):
        self.counts = {}
        self.episode = episode
        self.creatures = {}
        self.cells.fill(0)
        c = self.size * self.size
        for i in np.random.choice(c, int(grass_fraction * c)):
            self.set_cell(i // self.size, i % self.size, -1)

        for _ in range(START_NUM_CREATURES):
            x, y = self.free_spot()
            self.add_new_creature(GreedyCow(x, y, INIT_ENERGY, RED))
            x, y = self.free_spot()
            self.add_new_creature(DeepCow(x, y, INIT_ENERGY, YELLOW))

    def end(self):
        DeepCow.replay()

    def set_cell(self, x, y, value):
        self.cells[x, y] = value
        self.episode.grid_change(x, y, value)

    def free_spot(self):
        while True:
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if self.cells[x, y] == 0:
                return x, y

    def add_new_creature(self, creature):
        self.creatures[creature.id] = creature
        self.episode.creature_change(creature.id, creature.energy, type(creature).__name__)
        self.set_cell(creature.x, creature.y, creature.id)
        _, state, reward, done, _ = self.process_action(creature, Action.NONE)
        creature.learn(state, reward, done)

    def get_observation(self, creature):
        size_2 = self.size // 2
        rolled = np.roll(self.cells, (size_2 - creature.x, size_2 - creature.y), (0, 1))
        return rolled[size_2 - 1 : size_2 + 2, size_2 - 1 : size_2 + 2]

    def step(self):
        dead = set()
        born = []
        for creature in self.creatures.values():
            if creature.id in dead:
                continue

            action = creature.step(self.get_observation(creature))
            new_creature, state, reward, done, _ = self.process_action(creature, action)
            creature.learn(state, reward, done)

            if done:
                dead.add(creature)
            if new_creature:
                born.append(new_creature)

        for creature in dead:
            self.set_cell(creature.x, creature.y, 0)
            del self.creatures[creature.id]

        for creature in born:
            self.add_new_creature(creature)

        # Watching grass grow
        for _ in range(3):
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if self.cells[x, y] == 0:
                self.set_cell(x, y, -1)

        self.episode.next_frame()
        self.counts = Counter(creature.__class__.__name__ for creature in self.creatures.values())

        game_active = len(self.counts) == 2
        if not game_active:
            self.episode.save()
        return game_active

    def draw(self, display):
        for x in range(self.size):
            for y in range(self.size):
                idx = self.cells[x, y]
                if idx < 0:
                    color = (100, 240, 100)
                    display.rectangle(x, y, 1, color, padding=0.1)
                elif idx > 0:
                    self.creatures[idx].draw(display)

    def get_info(self):
        return ' '.join(k + ': ' + str(v) for k, v in self.counts.items())

    def apply_direction(self, option, x, y):
        dx, dy = option.to_direction()
        x = (x + dx) % self.size
        y = (y + dy) % self.size
        return x, y

    def process_action(self, creature, action):
        new_creature = None
        reward = 0
        if action == Action.NONE:
            creature.energy -= IDLE_COST
        elif action == Action.SPLIT:
            # Try to find an empty spot
            options = list(Action)[1:-1]  #
            random.shuffle(options)
            for option in options:
                x, y = self.apply_direction(option, creature.x, creature.y)
                if self.cells[x, y] == 0:
                    new_creature = creature.split()
                    reward = 10
                    break
        else:
            self.set_cell(creature.x, creature.y, 0)
            x, y = self.apply_direction(action, creature.x, creature.y)
            if self.cells[x, y] <= 0:
                if self.cells[x, y] == -1:
                    reward = 1
                    creature.energy += GRASS_ENERGY
                creature.x = x
                creature.y = y
            self.set_cell(creature.x, creature.y, creature.id)
            creature.energy -= MOVE_COST

        done = creature.energy < MIN_ENERGY

        creature_energy = creature.energy
        if done:
            creature_energy = 0
        creature_type = None
        if new_creature:
            creature_type = type(creature).__name__
        self.episode.creature_change(creature.id, creature_energy, creature_type)

        observation = self.get_observation(creature)
        return new_creature, observation, reward, done, {}

    def print(self):
        '''Prints the current screen as ascii chars to the console. Convenient for debugging.'''
        print('')
        print('  ', end='')
        for x in range(self.size):
            print(f'{x:>3}', end='')
        print()
        for y in range(self.size):
            print(f'{y:>2}' + ' ', end='')
            for x in range(self.size):
                if self.cells[x][y] == -1:
                    c = '.'
                elif self.cells[x][y] == 0:
                    c = ' '
                else:
                    c = 'C'
                print(' ' + c + ' ', end='')
            print()
