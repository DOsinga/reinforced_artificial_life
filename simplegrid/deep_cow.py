from simplegrid.cow import SimpleCow, Action, MAX_ENERGY
from simplegrid.dqn_agent import DQNAgent
from shared.constants import VIEW_DISTANCE
import numpy as np


class DeepCow(SimpleCow):
    agent = None

    def __init__(self, x, y, energy, color=None):
        super().__init__(x, y, energy, color)
        self.prev_state = None
        self.prev_reward = None
        self.prev_action_idx = None
        self.state = None
        self.reward = None
        self.done = None
        self.action_idx = 0

    def to_internal_state(self, observation):
        """Convert state to an internal representation.

        The input state is a NxN matrix with for each cell either a 1 for food,
        0 for nothing or -x for another animal. The center cell is always "us"
        """

        grass = np.copy(observation).flatten()
        grass[grass > 0] = 0
        grass[grass < 0] = 1
        cows = np.copy(observation).flatten()
        cows[cows < 0] = 0
        cows[cows > 0] = 1

        # Temporarily return a much simpler state, just the directions:
        # (up, right, down, left):
        return np.asarray([
            grass[3], grass[7], grass[5], grass[1]
        ])

        # return np.concatenate((grass, cows))

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        self.prev_state = self.state
        self.prev_reward = self.reward
        self.prev_action_idx = self.action_idx
        self.state = self.to_internal_state(observation)
        if not DeepCow.agent:
            DeepCow.agent = DQNAgent(len(self.state), action_size=4)
        self.action_idx = DeepCow.agent.act(self.state)
        if self.state[self.action_idx]:
            print(self.action_idx)
        return Action(self.action_idx + 1)

    def learn(self, reward, done):
        self.reward = reward
        if self.prev_state is not None and self.state is not None:
            DeepCow.agent.remember(self.prev_state, self.prev_action_idx, self.prev_reward, self.state)

    @classmethod
    def replay(cls):
        return DeepCow.agent.replay()
