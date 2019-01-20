import os

from simplegrid.cow import SimpleCow, Action, MAX_ENERGY
from simplegrid.dqn_agent import DQNAgent

import numpy as np

HISTORY_FILE = 'deep_cow_history.jsonl'
WEIGHTS_FILE = 'deep_cow_model_weights.h5'
MODEL_FILE = 'deep_cow_model.json'
YELLOW = (255, 255, 0)


class DeepCow(SimpleCow):
    agent = None

    def __init__(self, x, y, settings, energy=None):
        super().__init__(x, y, settings, energy)
        self.settings = settings
        self.color = YELLOW
        self.prev_state = None
        self.prev_reward = None
        self.prev_action_idx = None
        self.state = None
        self.reward = None
        self.done = None
        self.action_idx = 0

    @staticmethod
    def to_internal_state(observation):
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
        return np.asarray([grass[3], grass[7], grass[5], grass[1]])

        # return np.concatenate((grass, cows))

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        self.prev_state = self.state
        self.prev_reward = self.reward
        self.prev_action_idx = self.action_idx
        self.state = self.to_internal_state(observation)
        if not DeepCow.agent:
            DeepCow.agent = DQNAgent.from_dimensions(
                len(self.state), layers=self.settings.layers, action_size=4
            )
        self.action_idx = DeepCow.agent.act(self.state)
        return Action(self.action_idx + 1)

    def learn(self, reward, done):
        self.reward = reward
        if self.prev_state is not None and self.state is not None:
            DeepCow.agent.remember(
                self.prev_state, self.prev_action_idx, self.prev_reward, self.state
            )
            DeepCow.agent.replay()

    @classmethod
    def restore_state(cls, settings):
        model_file = settings.get_path(MODEL_FILE)
        if model_file and os.path.isfile(model_file):
            DeepCow.agent = DQNAgent.from_stored_model(model_file)
            DeepCow.agent.load_weights(settings.get_path(WEIGHTS_FILE))

    @classmethod
    def save_state(cls, settings):
        weights_file = settings.get_path(WEIGHTS_FILE)
        if weights_file:
            cls.agent.save_weights(weights_file)
            cls.agent.save_history(settings.get_path(HISTORY_FILE))
            cls.agent.save_model(settings.get_path(MODEL_FILE))
