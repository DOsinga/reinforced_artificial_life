import math
import random
import numpy as np

from model import SLICES

MAX_SPEED = 7
WANDER_SPEED = 3

# If total dx and dy is less than this amount, we deem the environment not interesting -> Go explore
INTERESTING = 5

# Not possible to eat creatures that are larger than this fraction of your own size
MAX_EATABLE_SIZE = .9

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

class Creature:
    """Creature class representing one bouncing ball for now."""
    id_count = 0

    def __init__(self, x, y, color, energy):
        self.x = x
        self.y = y
        self.color = color
        self.actioncolor = BLACK
        self.energy = energy
        self.id = Creature.id_count
        Creature.id_count += 1


    def step(self, nearby):
        if self.energy > 500:
            self.actioncolor = YELLOW
            return None

        flee = eat = 0
        slice_preference = np.zeros(SLICES)
        for other, slice, distance in nearby:
            assert type(slice) == type(1), "wrong type " + str(type(slice))
            assert slice>=0, "slice = "+ str(slice)
            assert slice < SLICES, "slice = "+ str(slice)
            distance_factor = 1/(distance+1)
            if isinstance(other, Creature) and other.energy > self.energy * MAX_EATABLE_SIZE:
                weight = 4*distance_factor
                flee += weight
                # Flee: update the slice at the other side
                slice = (slice + SLICES // 2) % SLICES
                assert type(slice) == type(1), "2wrong type " + str(type(slice))
                assert slice >= 0, "2slice = " + str(slice)
                assert slice < SLICES, "2slice = " + str(slice)
            else:
                weight = 2.2*distance_factor
                eat += weight
            slice_preference[slice] += weight
            # And the two slices next to that one
            slice_preference[(slice+1) % SLICES] += weight/2
            slice_preference[(slice-1) % SLICES] += weight/2

        chosen_slice = np.argmax(slice_preference)
        slice_weight = slice_preference[chosen_slice]

        if slice_weight < .4:
            # Nothing to get worked up about, go wander...
            self.actioncolor = BLUE
            chosen_slice = np.random.randint(SLICES)
            speed = WANDER_SPEED

        else:
            self.actioncolor = flee>eat and RED or GREEN
            speed = min(slice_weight*4, MAX_SPEED)

        return chosen_slice, speed

    def draw(self, display):
        display.circle(self.color, self.x, self.y, int(self.radius()))
        display.circle(self.actioncolor, self.x, self.y, 3)

    def box(self, box_size=None):
        """Return the bounding box for this creature"""
        if box_size is None:
            box_size = self.radius()
        res = [self.x - box_size, self.y - box_size, self.x + box_size, self.y + box_size]
        return res

    def distance(self, x1, y1):
        dx = self.x - x1
        dy = self.y - y1
        return math.sqrt(dx * dx + dy * dy)

    def radius(self):
        return math.sqrt(self.energy)

    def split(self):
        phi = random.uniform(0, math.pi * 2)
        dx = self.radius() * math.cos(phi)
        dy = self.radius() * math.sin(phi)
        new_creature = Creature(self.x + dx, self.y + dy, self.color, self.energy / 2)
        self.energy /= 2
        self.x -= dx
        self.y -= dy
        self.dx = -dx / 2
        self.dy = -dy / 2
        return new_creature

    def __repr__(self):
        return '\%02d/' % self.id
