#!/usr/bin/env python
import sys
import os
import argparse
import numpy as np
from simplegrid.cow import Action, GreedyCow, YELLOW, RED
from simplegrid.deep_cow import DeepCow
from shared.experiment_settings import ExperimentSettings

VERBOSE = True


def load_scenario(scenario_file):
    scenario = open(scenario_file).read()
    map, right_actions_string = scenario.split('\n\n')
    scenario_mapping = {char: idx - 1 for idx, char in enumerate('#.@')}
    observation = np.asarray(
        [[scenario_mapping[char] for char in list(line)] for line in map.split('\n')]
    ).T
    return observation, list(right_actions_string.rstrip())


def run_scenario(path, scenario_file, creature, repetitions=1):
    observation, right_actions = load_scenario(os.path.join(settings.path, scenario_file))
    right_actions = [Action.from_letter(ra) for ra in right_actions]
    result = 0
    for _ in range(repetitions):
        chosen_action = creature.step(observation)
        result += chosen_action in right_actions
    result_string = f'{100*result/repetitions:.0f}% passed'
    if VERBOSE:
        print()
        print('Scenario', scenario_file)
        print(observation.T)
        print('Right actions:', right_actions)
        print(result_string)
        print()
    else:
        print(scenario_file[:-13], result_string)
    return result / repetitions


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

    creature = DeepCow(0, 0, 100, YELLOW)
    # creature = GreedyCow(0,0,100,RED)

    right = 0
    for scenario_file in scenario_files:
        right += run_scenario(settings.path, scenario_file, creature, 1000)

    percentage = 100 * right / len(scenario_files)
    print(f'{right:.0f}/{len(scenario_files)} passed ({percentage:.0f}%)')
