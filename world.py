import random
import colorsys

from rtree import index

from creature import Creature, MAX_EATABLE_SIZE
from grass import Grass

GRASS_COUNT = 1000

# Creatures with less energy than this die
MIN_ENERGY = 100

# Fraction of energy lost each turn
ENERGY_LOSS = 0.001

# Fraction of eaten creature that is available for the eater
EAT_CREATURE_EFFICIENCY = .9


# How far can creatures 'see'
VISION_DISTANCE = 150

START_NUM_CREATURES = 4

def random_color():
    hue = random.uniform(0.5, 1.1) # random.uniform(0.0, 0.75)
    lightness = random.uniform(0.5, 0.8)
    saturation = random.uniform(0.7, 0.9)
    return tuple(map(lambda f: int(f * 255), colorsys.hls_to_rgb(hue, lightness, saturation)))


class World:
    """The world and the creatures in it. Also has an r-tree for collision detection."""
    def __init__(self, size):
        """Create a world with a size of size from the origin."""
        self.index = index.Index()
        self.size = size
        self.creatures = {}
        for _ in range(START_NUM_CREATURES):
            self.add_creature(self.random_creature())
        self.grass = {}
        while len(self.grass) < GRASS_COUNT:
            self.add_grass()

    def add_creature(self, creature):
        self.creatures[creature.id] = creature

    def del_creature(self, creature):
        del self.creatures[creature.id]

    def add_grass(self):
        grass = Grass(random.uniform(-1, 1) * self.size,
                      random.uniform(-1, 1) * self.size)
        self.grass[grass.id] = grass
        self.index.add(grass.id, grass.box())

    def step(self):
        # Watching grass grow
        for _ in range(5):
            self.add_grass()

        dead = set()
        born = []
        for creature in self.creatures.values():
            if creature.id in dead:
                continue
            # index deletion and addition has to be carefully balanced and take into account
            # changing energy levels:
            self.index.delete(creature.id, creature.box())
            nearby = self.nearby(creature)
            to_keep = []
            for real_distance, candidate in nearby:
                if real_distance < creature.radius() - candidate.radius():
                    # Dinner time
                    if isinstance(candidate, Grass):
                        creature.energy += 5
                        del self.grass[candidate.id]
                        self.index.delete(candidate.id, candidate.box())
                        continue
                    elif candidate.energy < creature.energy * MAX_EATABLE_SIZE:
                        dead.add(candidate)
                        creature.energy += candidate.energy * EAT_CREATURE_EFFICIENCY
                        continue
                to_keep.append(candidate)

            decision = creature.step(self, to_keep)
            if decision is None:
                born.append(creature.split())
            else:
                dx, dy = decision
                creature.x += dx
                creature.y += dy

            creature.energy *= (1 - ENERGY_LOSS)
            if creature.energy < MIN_ENERGY:
                dead.add(creature)
            self.index.add(creature.id, creature.box())

        # Bring out your dead - Grappig, ik wilde hetzelfde commentaar erbij zetten maar toen stond het er al :-)
        for creature in dead:
            del self.creatures[creature.id]
            self.index.delete(creature.id, creature.box())

        for creature in born:
            self.creatures[creature.id] = creature
            self.index.add(creature.id, creature.box())

    def draw(self, display):
        display.clear()
        for grass in self.grass.values():
            grass.draw(display)
        for creature in self.creatures.values():
            creature.draw(display)

    def random_creature(self):
        creature = Creature(random.uniform(-1, 1) * self.size, random.uniform(-1, 1) * self.size, color=random_color(),
                            energy=random.uniform(200, 600))
        return creature

    def indexed(self):
        return ' '.join(str(self.creatures[ci]) for ci in  self.index.intersection([-1000, -1000, 1000, 1000]))

    def nearby(self, creature):
        """Return any creature inside the circle (x,y) with the given radius."""
        res = []
        for candidate_id in self.index.intersection(creature.box(box_size=VISION_DISTANCE)):
            if candidate_id < 0:
                candidate = self.grass[candidate_id]
            else:
                candidate = self.creatures[candidate_id]
            real_distance = creature.distance(candidate.x, candidate.y)
            if real_distance < VISION_DISTANCE:
                res.append((real_distance, candidate))

        return res

    def get_info(self):
        return str(len(self.creatures))
