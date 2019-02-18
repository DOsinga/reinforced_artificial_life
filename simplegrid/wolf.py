import random
import operator

from simplegrid.abstractcreature import MAX_ENERGY, Action, AbstractCreature
from simplegrid.map_feature import MapFeature

WOLF_MOVE_SPEED = 0.5


class Wolf(AbstractCreature):

    COLOR = (101, 67, 33)
    IS_PREDATOR = True

    def step(self, observation):
        self.energy = MAX_ENERGY

        if random.random() > WOLF_MOVE_SPEED:
            return Action.NONE

        size = observation.shape[0]
        view_distance = size // 2
        possible_actions = {a: random.random() * 0.1 for a in list(Action)[1:-1]}

        for col in range(size):
            x = col - view_distance
            for row in range(size):
                y = row - view_distance
                dist = abs(x) + abs(y)
                value = observation[col, row]
                if 0 < dist <= view_distance:
                    if value == MapFeature.ROCK.index:
                        reward = -1
                    elif value == MapFeature.WATER.index:
                        reward = -100
                    elif value == MapFeature.COW.index:
                        reward = 10
                    elif value == MapFeature.WOLF.index:
                        reward = -100
                    else:
                        continue
                    reward /= dist * dist
                    if x < 0:
                        possible_actions[Action.LEFT] += reward
                    elif x > 0:
                        possible_actions[Action.RIGHT] += reward
                    if y < 0:
                        possible_actions[Action.UP] += reward
                    elif y > 0:
                        possible_actions[Action.DOWN] += reward
        best_action = max(possible_actions.items(), key=operator.itemgetter(1))[0]
        return best_action
