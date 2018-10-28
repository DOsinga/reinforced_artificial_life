import math
import random

MAX_SPEED = 7

class Creature:
    """Creature class representing one bouncing ball for now."""
    id_count = 0

    def __init__(self, x, y, color, energy):
        self.x = x
        self.y = y
        self.color = color
        self.energy = energy
        self.id = Creature.id_count
        Creature.id_count += 1

    def step(self, world, nearby):
        if self.energy > 50000:
            return None
        dx = 0
        dy = 0

        dist = self.distance(0, 0)
        if dist > world.size - self.radius():
            dx -= 0.05 * self.x / world.size
            dy -= 0.05 * self.y / world.size

        for other in nearby:
            dist = self.distance(other.x, other.y)
            if dist == 0:
                print(dist)
            if isinstance(other, Creature) and other.energy > self.energy:
                weight = -2
            else:
                weight = 2.2
            other_dx = (other.x - self.x) / dist
            other_dy = (other.y - self.y) / dist
            dx += other_dx * weight
            dy += other_dy * weight

        # Maximum speed:
        if abs(dx) > MAX_SPEED:
            dx *= MAX_SPEED / abs(dx)
        if abs(dy) > MAX_SPEED:
            dy *= MAX_SPEED / abs(dy)

        return dx, dy

    def draw(self, display):
        display.circle(self.color, self.x, self.y, int(self.radius()))

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
