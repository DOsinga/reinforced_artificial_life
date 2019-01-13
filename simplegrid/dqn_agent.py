import json
import random
import numpy as np

from collections import deque

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import Adam


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=5000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 0.8  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.5
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        """ Neural Net for Deep-Q learning Model--->>  #Q=NN.predict(state)"""
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        return model

    def remember(self, state, action, reward, next_state):
        """Store a memory

        Args:
            state: the state at the beginning of the action
            action: the chosen action based on this
            reward: the reward for the action
            next_state: the resulting state or None if the creature died.
        """
        self.memory.append((state, action, reward, next_state))

    def act(self, state):
        """
        Return an action given the state using the internal network.

        Args:
            state: flat array containing the state

        Returns:
            integer indicating the action

        """
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.predict(state)
        return np.argmax(act_values[0])

    def predict(self, state):
        state = np.reshape(state, (1, -1))
        return self.model.predict(state)

    def fit(self, state, target_f):
        state = np.reshape(state, (1, -1))
        self.model.fit(state, target_f, epochs=1, verbose=0)

    def replay(self):
        """Replay memories so older stuff doesn't get overwritten what we've learned.
        Also allows us to reinterpret experiences. Maybe dreaming works like this?
        """
        batch = [*self.memory]
        random.shuffle(batch)

        estimation_error_sum = 0

        for state, action, reward, next_state in batch:
            target = reward

            if next_state is not None:
                Q_next = self.predict(next_state)[0]
                target = reward + self.gamma * np.amax(Q_next)  # Belman

            target_f = self.predict(state)

            estimation_error_sum += abs(target_f[0][action] - target)
            target_f[0][action] = target

            # train network
            self.fit(state, target_f)

        self.epsilon = min(self.epsilon_decay * self.epsilon, self.epsilon_min)

        return estimation_error_sum / len(batch)

    def load_weights(self, name):
        self.model.load_weights(name)

    def save_weights(self, name):
        self.model.save_weights(name)

    def save_history(self, name):
        with open(name, 'w') as fout:
            for state, action, reward, next_state in self.memory:
                state = [float(x) for x in state]
                if next is not None:
                    next_state = [float(x) for x in next_state]
                record = {
                    'state': state,
                    'action': int(action),
                    'reward': float(reward),
                    'next_state': next_state,
                }
                fout.write(json.dumps(record) + '\n')
