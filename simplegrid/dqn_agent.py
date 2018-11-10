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
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 0.8  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model--->>  #Q=NN.predict(state)
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    # get action
    def act(self, state):

        # select random action with prob=epsilon else action=maxQ
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = np.reshape(state, (1, -1))
        act_values = self.predict(state)
        return np.argmax(act_values[0])  # returns action

    def predict(self, state):
        state = np.reshape(state, (1, -1))
        return self.model.predict(state)

    def fit(self, state, target_f):
        state = np.reshape(state, (1, -1))
        self.model.fit(state, target_f, epochs=1, verbose=0)

    def replay(self, batch_size):
        """Replay memories so older stuff doesn't get overwritten what we've learned.

        Also allows us to reinterprete experiences. Maybe dreaming works like this?
        """
        minibatch = random.sample(self.memory, batch_size)

        for state, action, reward, next_state, done in minibatch:
            target = reward

            if not done:
                # calculate target for each minibatch
                Q_next = self.predict(next_state)[0]
                target = reward + self.gamma * np.amax(Q_next)  # Belman

            target_f = self.predict(state)
            target_f[0][action] = target

            # train network
            self.fit(state, target_f)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
