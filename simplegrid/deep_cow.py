from simplegrid.cow import SimpleCow, Action, MAX_ENERGY
from simplegrid.dqn_agent import DQNAgent
from shared.constants import VIEW_DISTANCE
import numpy as np

class DeepCow(SimpleCow):
    agent = None

    def __init__(self, x, y, energy, color=None):
        super().__init__(x, y, energy, color)
        self.state = None
        self.action_idx = 0

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        self.action_idx = DeepCow.agent.act(self.state)
        return Action(self.action_idx + 1)

    def to_internal_state(self, state):
        """Convert state to an internal representation.

        The input state is a NxN matrix with for each cell either a 1 for food,
        0 for nothing or -x for another animal. The center cell is always "us"
        """

        grass = np.copy(state).flatten()
        grass[grass <= 0] = 0
        cows = np.copy(state).flatten()
        cows[cows >= 0] = 0
        cows[cows < 0] = 1

        return np.concatenate((grass, cows))

    def learn(self, state, reward, done):
        state = self.to_internal_state(state)
        if not DeepCow.agent:
            DeepCow.agent = DQNAgent(len(state), action_size=4)

        if self.state is not None:
            DeepCow.agent.remember(self.state, self.action_idx, reward, state, done)
        self.state = state

    @classmethod
    def replay(cls):
        return DeepCow.agent.replay()
