import json
import random
import numpy as np

from collections import deque

from tensorflow.python.keras.models import Sequential, model_from_json
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import Adam


class DQNAgent:
    def __init__(self, model, epsilon):
        """Create an agent using a model. Typically you want to call either from_stored_model or from_dimensions."""
        self.memory = deque(maxlen=5000)
        self.gamma = 0.95  # discount rate
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.5
        self.learning_rate = 0.001
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        self.model = model

    @classmethod
    def from_stored_model(cls, model_file):
        model_and_settings = json.load(open(model_file))
        epsilon = model_and_settings['epsilon']
        model_json = model_and_settings['model']
        model = model_from_json(json.dumps(model_json))

        return cls(model, epsilon)

    @classmethod
    def from_dimensions(cls, state_size, action_size):
        """ Neural Net for Deep-Q learning Model--->>  #Q=NN.predict(state)"""
        model = Sequential()
        model.add(Dense(24, input_dim=state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(action_size, activation='linear'))

        return cls(model, epsilon=0.8)

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
            output_size = self.model.output.shape[-1]
            return random.randrange(output_size)
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
        print(self.identity_test())

        batch = [*self.memory]
        random.shuffle(batch)

        estimation_error_sum = 0

        for state, action, reward, next_state in batch:
            target = reward

            if next_state is not None:
                Q_next = self.predict(next_state)[0]
                target = reward + self.gamma * np.amax(Q_next)  # Bellman

            target_f = self.predict(state)

            estimation_error_sum += abs(target_f[0][action] - target)
            target_f[0][action] = target

            # train network
            self.fit(state, target_f)

        self.epsilon = min(self.epsilon_decay * self.epsilon, self.epsilon_min)
        print(self.identity_test())

        return estimation_error_sum / len(batch)

    def identity_test(self):
        """Run the network over inputs with each exactly one cell set to one."""
        input_size = int(self.model.input.shape[-1])
        inputs = np.zeros((input_size, input_size))
        for i in range(input_size):
            inputs[i][i] = 1.0
        return self.model.predict(inputs)

    def load_weights(self, name):
        self.model.load_weights(name)
        print(self.identity_test())

    def save_weights(self, name):
        self.model.save_weights(name)
        print(self.identity_test())

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

    def save_model(self, name):
        model_json = json.loads(self.model.to_json(indent=2))
        with open(name, 'w') as json_file:
            json.dump({'model': model_json, 'epsilon': self.epsilon}, json_file)
