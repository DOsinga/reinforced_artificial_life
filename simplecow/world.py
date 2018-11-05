import colorsys
import random
from enum import IntEnum
from dataclasses import dataclass

from cow import Cow, GreedyCow, Action, MAX_ENERGY, MIN_ENERGY
from grass import Grass


GRASS_RATIO = .2
START_NUM_CREATURES = 8

# Fraction of energy lost each turn
ENERGY_LOSS = 0.001

# How far can creatures 'see'
VISION_DISTANCE = 2

def random_color(hue=None):
    if not hue:
        hue = random.uniform(0.5, 1.1)
    lightness = random.uniform(0.5, 0.8)
    saturation = random.uniform(0.7, 0.9)
    return tuple(map(lambda f: int(f * 255), colorsys.hls_to_rgb(hue, lightness, saturation)))


def action2dxdy( action ):
    return {Action.RIGHT: (1, 0),
            Action.LEFT: (-1, 0),
            Action.DOWN: (0, 1),
            Action.UP: (0,-1)}.get(action)

class CellType(IntEnum):
    EMPTY = 0
    GRASS = 1
    COW = 2

    def __repr__(self):
        return self.name

@dataclass
class Cell():
    celltype: CellType = CellType.EMPTY
    contents: object = None

    def set(self, celltype, contents=None ):
        self.celltype = celltype
        self.contents = contents


class World:
    """The world and the creatures in it. Also has an r-tree for collision detection."""

    def __init__(self, size):
        """Create a world with a size of size """

        self.size = size
        self.grid =  [[Cell() for x in range(size)] for y in range(size)]

        self.creatures = {}
        for _ in range(START_NUM_CREATURES//2):

            cow = Cow(
                random.randint(0, self.size - 1), random.randint(0, self.size - 1),
                color=random_color(.5),
                energy=20,
            )
            greedycow = GreedyCow(
                random.randint(0, self.size - 1), random.randint(0, self.size - 1),
                color=random_color(.9),
                energy=20,
            )
            self.add_creature(cow)
            self.add_creature(greedycow)

        self.grass = {}
        while len(self.grass) < GRASS_RATIO * self.size * self.size:
            self.add_grass()


    def add_creature(self, creature):
        self.creatures[creature.id] = creature
        self.grid[creature.x][creature.y].set( CellType.COW, creature )

    def del_creature(self, creature):
        del self.creatures[creature.id]

    def add_grass(self):

        x = random.randrange(0, self.size)
        y = random.randrange(0, self.size)
        if self.grid[x][y].celltype != CellType.EMPTY:
            return

        grass = Grass(x,y)
        self.grass[grass.id] = grass
        self.grid[x][y].set( CellType.GRASS, grass )


    def step(self):
        dead = set()
        born = []
        for creature in self.creatures.values():
            if creature.id in dead:
                continue

            nearby = self.nearby(creature)
            action = creature.step(nearby)

            if action is Action.SPLIT:
                born.append(creature.split())
            else:
                # dx, dy = decision

                dx, dy = action2dxdy( action )

                dx = min(dx,self.size-1-creature.x)
                dx = max(dx, -creature.x)
                dy = min(dy,self.size-1-creature.y)
                dy = max(dy, -creature.y)

                self.grid[creature.x][creature.y].set( CellType.EMPTY )
                creature.x += dx
                creature.y += dy
                if self.grid[creature.x][creature.y].celltype == CellType.GRASS:
                    # Eat
                    creature.energy += 5
                    grass = self.grid[creature.x][creature.y].contents
                    del self.grass[grass.id]
                self.grid[creature.x][creature.y].set(CellType.COW, creature)

            creature.energy -= 1
            if creature.energy < MIN_ENERGY:
                dead.add(creature)

        # Bring out your dead
        for creature in dead:
            self.grid[creature.x][creature.y].set(CellType.EMPTY)
            del self.creatures[creature.id]

        for creature in born:
            x = creature.x
            y = creature.y
            # Find new spot
            while self.grid[x][y].celltype != CellType.EMPTY:
                print( x,y, )
                x = max(0,min(self.size-1,x+random.randint(-1, 1)))
                y = max(0,min(self.size-1,y+random.randint(-1,1)))
            self.grid[x][y].set( CellType.COW, creature )
            self.creatures[creature.id] = creature

        # Watching grass grow
        for _ in range(3):
            self.add_grass()



    def draw(self, display):
        display.clear()
        for grass in self.grass.values():
            grass.draw(display)
        for creature in self.creatures.values():
            creature.draw(display)

    def random_creature(self):
        x = random.randint(0, self.size - 1)
        y = random.randint(0, self.size - 1)
        cow = GreedyCow(
            x,y,
            color=random_color(),
            energy=random.uniform(15, 20),
        )
        return cow


    def nearby(self, creature):
        """Return a list of (cell,x,y) tuples of all non emtpy cells within viewing distance"""
        res = []
        for x in range( max(0, creature.x - VISION_DISTANCE), min(self.size, creature.x + VISION_DISTANCE + 1) ):
            for y in range( max(0, creature.y - VISION_DISTANCE), min(self.size, creature.y + VISION_DISTANCE + 1) ):
                if (x != creature.x or y != creature.y)  and self.grid[x][y].celltype!=CellType.EMPTY:
                    res.append((self.grid[x][y], x, y))
        return res

    def get_info(self):
        return str(len(self.creatures))

    def print(self):
        '''Prints the current screen as ascii chars to the console. Convenient for debugging.'''
        print('')
        print('  ', end='')
        for x in range(self.size):
            print( f'{x:>3}', end='' )
        print()
        for y in range( self.size ):
            print( f'{y:>2}' + ' ', end='' )
            for x in range( self.size ):
                index = int(self.grid[x][y].celltype)
                print( ' ' + '.gC'[index] + ' ', end='')
            print()

