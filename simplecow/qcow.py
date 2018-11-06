import random
import numpy as np

from simplecow.cow import Cow, VISION_DISTANCE, Action
from simplecow.qmodel import get_model

epsilon = 0.1


class QCow(Cow):
    def __init__(self, x, y, color, energy, lineage=0):
        super().__init__(x, y, color, energy)
        self.lineage = lineage
        self.model = get_model(lineage)
        print('q-table size', len(self.model.Q_table))

    def action(self, nearby):
        state = self.nearby2state(nearby)

        if random.random() < epsilon:
            return super().action(nearby)
        else:
            action_values = self.model.Q_values(state)
            maximum = np.amax(action_values)
            maxima = np.where(action_values == maximum)[0]
            actionint = random.choice(list(maxima))  # select the action with the highest value
            action = Action(actionint)

        self._last_state_action = (state, action)
        return action

    def nearby2state(self, nearby):
        # Nearby is list of cel, x, y of all nearby non-empty cells
        # Works only if VISION_DISTANCE == 2
        statecells = [
            (0, 2),
            (-1, 1),
            (0, 1),
            (1, 1),
            (-2, 0),
            (-1, 0),
            (1, 0),
            (2, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (0, -2),
        ]

        state = [0] * 12
        for cell, x, y in nearby:
            dx = x - self.x
            dy = y - self.y
            try:
                stateindex = statecells.index((dx, dy))
                state[stateindex] = int(cell.celltype)
            except ValueError:
                # Index raises an error if needle is not found
                # which is just fine here. No action to be taken
                # in the except clauase
                pass
        return tuple(state)

    def reward(self, reward):
        if hasattr(self, '_last_state_action'):
            # Ugly code. Needs change When last action was SPLIT no _last_state_action was set
            self.model.updateQtable(self._last_state_action, reward)
