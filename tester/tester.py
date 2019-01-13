import numpy as np
from simplegrid.cow import Action
from simplegrid.dqn_agent import DQNAgent
import shared.constants
from simplegrid.deep_cow import DeepCow

scenario_mapping = {char: idx - 1 for idx, char in enumerate('#.@')}


def load_scenario(scenario_file):
    scenario = open(scenario_file).read()
    map, right_actions_string = scenario.split('\n\n')
    observation = np.asarray(
        [[scenario_mapping[char] for char in list(line)] for line in map.split('\n')]
    )
    state = DeepCow.to_internal_state(observation)
    return state, list(right_actions_string.rstrip())


def load_agent(state_size):
    agent = DQNAgent(state_size, action_size=4)
    weight_file = (
        '../state/last_model_weights.h5'
    )  # constants.state_pattern.format(filename=constants.WEIGHTS_FILE)
    agent.load_weights(weight_file)
    return agent


if __name__ == '__main__':
    state, right_actions = load_scenario('left.txt')
    print(state)
    print('Preferred actions:', right_actions)
    agent = load_agent(len(state))

    action_idx = agent.act(state)
    chosen_action = Action(action_idx + 1)
    print('Chosen action:', chosen_action)
