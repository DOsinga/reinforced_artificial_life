import random
import numpy as np

from simplecow.cow import Cow, VISION_DISTANCE, Action
from simplecow.qmodel import get_model

epsilon = .1

class QCow( Cow ):

    def __init__(self, x, y, color, energy, lineage=0):
        super().__init__( x,y, color, energy)
        self.lineage = lineage
        self.model = get_model( lineage )
        print(len(self.model.Q_table ))

    def action(self, nearby):
        state = self.nearby2state( nearby )

        if random.random() < epsilon:
            action = random.choice(list(Action)[1:-1])
        else:
            action_values = self.model.Q_values(state)
            action = Action(np.argmax(action_values))  # select the action with the highest value

        self._last_state_action = (state, action)
        return action

    def nearby2state(self, nearby):
        # Nearby is list of cel, x, y of all nearby non-empty cells
        # Works only if VISION_DISTANCE == 2
        statecells = [  (0, 2),
               (-1, 1), (0, 1), (1, 1),
       (-2,0), (-1, 0),         (1, 0), (2, 0),
               (-1,-1), (0,-1), (1,-1),
                        (0,-2)]

        state = [0] * 12
        for cell, x, y in nearby:
            dx = x - self.x
            dy = y - self.y
            try:
                stateindex = statecells.index((dx,dy))
                state[stateindex] = int(cell.celltype)
            except:
                pass
        return tuple(state)

    def reward(self, reward):
        self.model.updateQtable( self._last_state_action, reward )


