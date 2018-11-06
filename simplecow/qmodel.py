from simplecow.cow import Action
from dataclasses import dataclass

models = {}  # Dict of key:QModel to keep track of the various incarnations of the model


def get_model(lineage):
    ''' Returs the model for the given lineage. If it does not exist yet, create it '''
    model = models.get(lineage)
    if not model:
        model = QModel()
        models[lineage] = model
    return model


# QEntries are the values in the Q-table
@dataclass()
class QEntry:
    count: int = 0
    value: float = 0.0


class QModel:
    def __init__(self):
        # Q_table is a dict of all known state+action -> value cominations.
        # dict keys: (state, action) tuples
        # dict values: QEntry(count, value) object
        self.Q_table = {}

    def increaseCount(self, state_action):
        if not self.Q_table.get(state_action):
            self.Q_table[state_action] = QEntry()
        self.Q_table[state_action].count += 1
        return self.Q_table[state_action].count

    def updateQtable(self, state_action, reward):
        ''' Recalculates the average rewards for the Q-value look-up table '''
        newcount = self.increaseCount(state_action)
        curvalue = self.Q_table[state_action].value
        increment = (reward - curvalue) / newcount
        self.Q_table[state_action].value += increment

    # Returns Q-value/avg rewards for each action given a state
    def Q_values(self, state):
        res = []
        for action in list(Action)[:-1]:
            qentry = self.Q_table.get((state, action))
            if qentry:
                res += [qentry.value]
            else:
                res += [0]
        return res

    def __str__(self):
        return "\n".join(
            [str(key) + ' : ' + str(self.Q_table[key]) for key in self.Q_table.keys()]
        )
