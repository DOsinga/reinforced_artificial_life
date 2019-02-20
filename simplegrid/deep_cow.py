import os
import numpy as np

from simplegrid.abstractcreature import MAX_ENERGY, Action, AbstractCreature
from simplegrid.dqn_agent import DQNAgent
from simplegrid.map_feature import MapFeature

HISTORY_FILE = 'deep_cow_history.jsonl'
WEIGHTS_FILE = 'deep_cow_model_weights.h5'
MODEL_FILE = 'deep_cow_model.json'


class DeepCow(AbstractCreature):
    agent = None
    COLOR = (240, 240, 20)
    IS_PREDATOR = False

    def __init__(self, x, y, settings, energy=None):
        super().__init__(x, y, settings, energy)
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

        The input state is a (2 x d + 1, 2 x d + 1) matrix with for each
        cell either a 1 for food, 0 for nothing or -x for another animal.
        The center cell is always "us". Only the largest diamond fitting
        the matrix is actually visible.
        """
        size = observation.shape[0]

        view_distance = size // 2
        if view_distance == 1:
            diamond = observation.flatten()
            diamond = [diamond[3], diamond[7], diamond[5], diamond[1]]
        else:
            diamond = []
            for x in range(size):
                for y in range(size):
                    if 0 < abs(x - size // 2) + abs(y - size // 2) <= view_distance:
                        diamond.append(observation[x][y])
        diamond = np.asarray(diamond)

        grass = MapFeature.GRASS.to_feature_vector(diamond)
        rock = MapFeature.ROCK.to_feature_vector(diamond)

        water = MapFeature.ROCK.to_feature_vector(diamond)
        wolves = MapFeature.WOLF.to_feature_vector(diamond)
        return np.concatenate((grass, rock, water, wolves))

    def step(self, observation):
        if self.energy > MAX_ENERGY:
            return Action.SPLIT

        self.prev_state = self.state
        self.prev_reward = self.reward
        self.prev_action_idx = self.action_idx
        self.state = self.to_internal_state(observation)
        if not DeepCow.agent:
            DeepCow.agent = DQNAgent.from_dimensions(len(self.state), layers=self.settings.layers, action_size=4)
        self.action_idx = DeepCow.agent.act(self.state)
        return Action(self.action_idx + 1)

    def learn(self, reward, done):
        self.reward = reward
        if self.prev_state is not None and self.state is not None:
            DeepCow.agent.remember(self.prev_state, self.prev_action_idx, self.prev_reward, self.state)
            DeepCow.agent.replay()
        if done:
            DeepCow.agent.remember(self.state, self.action_idx, self.reward, None)

    @classmethod
    def restore_state(cls, settings):
        model_file = settings.get_path(MODEL_FILE)
        if model_file and os.path.isfile(model_file):
            DeepCow.agent = DQNAgent.from_stored_model(model_file)
            weights_file = settings.get_path(WEIGHTS_FILE)
            if weights_file and os.path.isfile(weights_file):
                DeepCow.agent.load_weights(weights_file)

    @classmethod
    def save_state(cls, settings):
        weights_file = settings.get_path(WEIGHTS_FILE)
        if weights_file:
            cls.agent.save_weights(weights_file)
            cls.agent.save_history(settings.get_path(HISTORY_FILE))
            cls.agent.save_model(settings.get_path(MODEL_FILE))
