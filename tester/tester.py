#!/usr/bin/env python
import sys
import os
import argparse
import numpy as np
from simplegrid.cow import Action
from simplegrid.dqn_agent import DQNAgent
from simplegrid.deep_cow import DeepCow, MODEL_FILE, WEIGHTS_FILE
from shared.experiment_settings import ExperimentSettings

from simplegrid.cow import Action
from simplegrid.dqn_agent import DQNAgent
from simplegrid.deep_cow import DeepCow


def load_scenario(scenario_file):
    scenario = open(scenario_file).read()
    map, right_actions_string = scenario.split('\n\n')
    scenario_mapping = {char: idx - 1 for idx, char in enumerate('#.@')}
    observation = np.asarray(
        [[scenario_mapping[char] for char in list(line)] for line in map.split('\n')]
    )
    state = DeepCow.to_internal_state(observation)
    return state, list(right_actions_string.rstrip())


def load_agent(path):
    agent = DQNAgent.from_stored_model(os.path.join(path, MODEL_FILE))
    weight_file = os.path.join(path, WEIGHTS_FILE)
    agent.load_weights(weight_file)
    return agent


def run_scenario(path, scenario_file):
    state, right_actions = load_scenario(os.path.join(settings.path, scenario_file))
    print()
    print('Scenario', scenario_file)
    print(state)
    right_actions = [Action.from_letter(ra) for ra in right_actions]
    print('Right actions:', right_actions)

    agent = load_agent(path)
    action_idx = agent.act(state)
    chosen_action = Action(action_idx + 1)
    print('Chosen action:', chosen_action)
    result = chosen_action in right_actions
    print(result and 'Passed' or 'Failed')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--experiment',
        type=str,
        required=True,
        help='Optional argument specifying the experiment to run. This should be a directory '
        'where the specific settings and various state files are stored. Directoy will '
        'be created and initialized if it does not exist.',
    )
    args = parser.parse_args()
    settings = ExperimentSettings(args.experiment)
    print('Testing experiment', settings.path)


    scenario_files = [file for file in os.listdir(settings.path) if file.endswith(".scenario.txt")]
    if not scenario_files:
        print('No scenarios found in', settings.path)
        sys.exit()

    for scenario_file in scenario_files:
        run_scenario(settings.path, scenario_file)

