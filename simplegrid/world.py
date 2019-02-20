#!/usr/bin/env python
import os
import random
from collections import Counter, defaultdict, deque

import numpy as np

from simplegrid.cow import Action, SmartCow
from simplegrid.deep_cow import DeepCow
from simplegrid.map_feature import MapFeature


class World:
    def __init__(self, settings, display):
        self.counts = {}
        display.offset_x = 0
        display.offset_y = 0
        if settings.path:
            display.sidebar[os.path.basename(os.path.normpath(settings.path))] = ''

        self.creatures = {}
        self.energies = {}
        self.settings = settings
        self.size = settings.world_size
        # cells has two layers, one for grass, one for what's on grass:
        self.cells = np.zeros((self.size, self.size, 2))
        self.steps = 0
        self.winstreak = deque(maxlen=9)
        DeepCow.restore_state(settings)

    def reset(self, *, grass_fraction=None, rock_fraction=None, water_fraction=None):
        if grass_fraction is None:
            grass_fraction = self.settings.start_grass_fraction
        if rock_fraction is None:
            rock_fraction = self.settings.start_rock_fraction
        if water_fraction is None:
            water_fraction = self.settings.start_water_fraction
        self.counts = {}
        self.creatures = {}
        self.cells.fill(0)
        self.steps = 0
        c = self.size * self.size
        rock_count = int(c * rock_fraction)
        water_count = int(c * water_fraction)
        for x in range(self.size):
            for y in range(self.size):
                self.cells[x, y, 0] = min(1.0, random.uniform(grass_fraction * 0.8, grass_fraction * 1.2))

        for idx_choice, idx_val in enumerate(np.random.choice(c, rock_count + water_count, replace=False)):
            if idx_choice <= rock_count:
                celltype = MapFeature.ROCK
            else:
                celltype = MapFeature.WATER
            self.set_object(idx_val // self.size, idx_val % self.size, celltype.index)

        for _ in range(self.settings.start_num_creatures):
            x, y = self.free_spot()
            self.add_new_creature(SmartCow(x, y, self.settings))
            x, y = self.free_spot()
            self.add_new_creature(DeepCow(x, y, self.settings))

    def end(self, show_weights=False):
        DeepCow.save_state(self.settings)
        print('deep-cow-loss:', DeepCow.agent.replay())
        if show_weights:
            DeepCow.agent.show_weights()

    def set_object(self, x, y, value):
        self.cells[x, y, 1] = value

    def free_spot(self):
        while True:
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if self.cells[x, y, 1] == 0:
                return x, y

    def add_new_creature(self, creature):
        self.creatures[creature.id] = creature
        self.set_object(creature.x, creature.y, creature.id)

    def get_observation(self, creature):
        size_2 = self.size // 2
        rolled = np.roll(self.cells, (size_2 - creature.x, size_2 - creature.y), (0, 1))
        view_distance = self.settings.view_distance
        return rolled[
            size_2 - view_distance : size_2 + view_distance + 1, size_2 - view_distance : size_2 + view_distance + 1
        ]

    def step(self):
        self.steps += 1
        if self.steps == self.settings.steps_per_episode:
            return self.end_of_episode()
        dead = set()
        born = []
        self.energies = defaultdict(int)
        for creature in self.creatures.values():
            if creature.id in dead:
                continue

            observation = self.get_observation(creature)
            action = creature.step(observation)
            new_creature, reward, done = self.process_action(creature, action)
            creature.learn(reward, done)

            if done:
                dead.add(creature)
            if new_creature:
                born.append(new_creature)

            self.energies[creature.__class__.__name__] += creature.energy

        for creature in dead:
            self.set_object(creature.x, creature.y, 0)
            del self.creatures[creature.id]

        for creature in born:
            self.add_new_creature(creature)

        growth = self.settings.grass_grow_per_turn
        for x in range(self.size):
            for y in range(self.size):
                self.cells[x, y, 0] = min(1.0, self.cells[x, y, 0] + growth)

        self.counts = Counter(creature.__class__.__name__ for creature in self.creatures.values())

        if not len(self.counts) == 2:
            return self.end_of_episode()
        return True

    def end_of_episode(self):
        if len(self.counts) == 0:
            print('draw')
            winner = '-'
        else:
            winner = list(self.counts.elements())[0]
            print(winner, 'wins')
        self.winstreak.append(winner[0])
        return False

    def draw(self, display):
        grass_mass = 0
        for x in range(self.size):
            for y in range(self.size):
                grass = self.cells[x, y, 0]

                def interpolate(f):
                    return int(20 * (1 - grass) + grass * f)

                grass_mass += grass
                display.rectangle(x, y, 1, (interpolate(20), interpolate(240), interpolate(20)), padding=0)

                idx = self.cells[x, y, 1]
                if idx < 0:
                    display.rectangle(x, y, 1, MapFeature(idx).color, padding=0.1)
                elif idx > 0:
                    self.creatures[idx].draw(display)
        display.sidebar['Winner streak'] = ''.join(self.winstreak)
        display.sidebar['steps'] = self.steps
        display.sidebar['grass'] = str(round(100 * grass_mass / self.size / self.size)) + '%'
        for k, v in self.counts.items():
            display.sidebar[k + 's'] = v
            display.sidebar[k + ' energy'] = int(self.energies[k])

    def get_info(self):
        return ' '.join(k + ': ' + str(v) for k, v in self.counts.items())

    def apply_direction(self, option, x, y):
        dx, dy = option.to_direction()
        x = (x + dx) % self.size
        y = (y + dy) % self.size
        return x, y

    def process_action(self, creature, action):
        new_creature = None
        reward = 0  # -self.settings.move_cost / self.settings.grass_energy
        if action == Action.GRAZE:
            graze = min(self.cells[creature.x, creature.y, 0], 0.2)
            self.cells[creature.x, creature.y, 0] -= graze
            reward += graze
            creature.energy += self.settings.grass_energy * graze - self.settings.idle_cost
        elif action == Action.SPLIT:
            # Split, try to find an empty spot
            options = list(Action)[1:-1]
            random.shuffle(options)
            for option in options:
                x, y = self.apply_direction(option, creature.x, creature.y)
                if self.cells[x, y, 1] == 0:
                    new_creature = creature.split()
                    break
        else:
            # Move
            self.set_object(creature.x, creature.y, 0)
            x, y = self.apply_direction(action, creature.x, creature.y)
            if self.cells[x, y, 1] == MapFeature.EMPTY.index:
                creature.x = x
                creature.y = y
            self.set_object(creature.x, creature.y, creature.id)
            creature.energy -= self.settings.move_cost
            if self.cells[x, y, 1] == MapFeature.WATER.index:
                creature.energy = 0
        done = creature.energy < self.settings.min_energy

        return new_creature, reward, done

    def print(self):
        """Prints the current screen as ascii chars to the console. Convenient for debugging."""
        print('')
        print('  ', end='')
        for x in range(self.size):
            print(f'{x:>3}', end='')
        print()
        for y in range(self.size):
            print(f'{y:>2}' + ' ', end='')
            for x in range(self.size):
                mf = MapFeature(max(1, self.cells[x][y][1]))
                print(f' {mf.char} ', end='')
            print()
