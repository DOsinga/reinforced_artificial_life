import random
import operator

from simplegrid.abstractcreature import MAX_ENERGY, Action, AbstractCreature
from simplegrid.map_feature import MapFeature


class SimpleCow(AbstractCreature):

    COLOR = (120, 240, 20)

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        return random.choice(list(Action)[1:-1])


class GreedyCow(AbstractCreature):

    COLOR = (240, 20, 20)

    def step(self, observation):

        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        offset = observation.shape[0] // 2
        possible_actions = list(Action)[1:-1]
        interesting_actions = [a for a in possible_actions if observation[a.to_observation(offset)] == -1]

        if interesting_actions:
            return random.choice(interesting_actions)
        else:
            return Action.RIGHT  # Was: random.choice(possible_actions)


class SmartCow(SimpleCow):

    COLOR = (240, 120, 20)

    def step(self, observation):

        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        size = observation.shape[0]
        view_distance = size // 2
        possible_actions = {a: 0.0 for a in list(Action)[1:-1]}

        for col in range(size):
            x = col - view_distance
            for row in range(size):
                y = row - view_distance
                dist = abs(x) + abs(y)
                value = observation[col, row]
                if 0 < dist <= view_distance:
                    if value == MapFeature.GRASS.index:
                        reward = 1
                    elif value == MapFeature.ROCK.index:
                        reward = -1
                    elif value == MapFeature.COW.index:
                        reward = -0.5
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
