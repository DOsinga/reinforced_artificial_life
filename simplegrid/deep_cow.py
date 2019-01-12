from simplegrid.cow import SimpleCow, Action, MAX_ENERGY
from simplegrid.dqn_agent import DQNAgent
from shared.constants import VIEW_DISTANCE


class DeepCow(SimpleCow):
    state_size = (2 * VIEW_DISTANCE + 1) * (2 * VIEW_DISTANCE + 1)
    agent = DQNAgent(state_size, action_size=4)

    def __init__(self, x, y, energy, color=None):
        super().__init__(x, y, energy, color)
        self.state = None
        self.action_idx = 0

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        self.action_idx = DeepCow.agent.act(self.state)
        return Action(self.action_idx + 1)

    def learn(self, state, reward, done):
        if self.state is not None:
            DeepCow.agent.remember(self.state, self.action_idx, reward, state, done)
        self.state = state

    @classmethod
    def replay(cls):
        return DeepCow.agent.replay()
