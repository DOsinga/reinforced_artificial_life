from simplegrid.cow import SimpleCow, Action, MAX_ENERGY
from simplegrid.dqn_agent import DQNAgent

BATCH_SIZE = 32

class DeepCow(SimpleCow):
    agent = DQNAgent(9, 5)

    def __init__(self, x, y, energy, color=None):
        super().__init__(x, y, energy, color)
        self.state = None
        self.action = Action.NONE

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        action_idx = DeepCow.agent.act(self.state)

        self.action = Action(action_idx + 1)
        return self.action

    def learn(self, state, reward, done):
        DeepCow.agent.remember(self.state, self.action, reward, state, done)
        self.state = state

    @classmethod
    def replay(cls):
        if len(DeepCow.agent.memory) > BATCH_SIZE:
            DeepCow.agent.replay(BATCH_SIZE)

