import math

from simplegrid.cow import SimpleCow, Action
from simplegrid.dqn_agent import DQNAgent

MAX_ENERGY = 1000


class DeepCow(SimpleCow):
    agent = DQNAgent(9, 4)

    def __init__(self, x, y, energy, color=None):
        super().__init__(x, y, energy, color)
        self.state = None
        self.action = Action.NONE

    def step(self):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        action_idx = DeepCow.agent.act(self.state)

        self.action = Action(action_idx + 1)
        return self.action

    def learn(self, state, reward, done):
        DeepCow.agent.remember(self.state, self.action, reward, state, done)
        self.state = state

    def draw(self, display):
        display.circle(
            self.color, self.x, self.y, 3 * min(1, math.sqrt(2 * self.energy / MAX_ENERGY))
        )
