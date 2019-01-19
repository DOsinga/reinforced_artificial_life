#!/usr/bin/env python
import sys
import os
import argparse
import numpy as np

sys.path.append('..')
from simplegrid.cow import Action, GreedyCow
from simplegrid.deep_cow import DeepCow
from shared.experiment_settings import ExperimentSettings

TESTS_DIR = 'tests'
SCENARIO_MAPPING = {char: idx - 1 for idx, char in enumerate('#.@')}
CREATURES = {'greedy': GreedyCow, 'deep': DeepCow}


def load_scenario(scenario_file):
    scenario = open(scenario_file).read()
    map, right_actions_string = scenario.split('\n\n')
    observation = np.asarray(
        [[SCENARIO_MAPPING[char] for char in list(line)] for line in map.split('\n')]
    ).T
    right_actions = [Action.from_letter(ra) for ra in list(right_actions_string.rstrip())]
    return observation, right_actions


def run_scenario(scenario, creature, verbose, repetitions=1):
    observation, right_actions = load_scenario(scenario)
    result = 0
    chosen_actions = []
    for _ in range(repetitions):
        chosen_action = creature.step(observation)
        chosen_actions += [chosen_action]
        result += chosen_action in right_actions
    result_string = f'{100*result/repetitions:4.0f}% passed'
    if verbose:
        print()
        print('Scenario', scenario)
        print(observation.T)
        print('Right actions:', right_actions)
        print('Chosen actions:', chosen_actions[:20])
        print(result_string)
        print()
    else:
        print(f'{scenario:<25} {result_string}')
    return result / repetitions


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--experiment',
        type=str,
        required=True,
        help='Required argument specifying the experiment to run. This should be a directory '
        'where the specific settings and various state files are stored. Directoy will '
        'be created and initialized if it does not exist.',
    )
    parser.add_argument(
        '--creature',
        type=str,
        choices=list(CREATURES),
        required=True,
        help='Required argument that specifies wich creature will be tested. Options are greedy or deep.',
    )
    parser.add_argument(
        '--test',
        type=str,
        required=False,
        help='Optional argument specifying the test to run. This should be an existing '
        'file name in the tests diretory without the path.',
    )
    parser.add_argument(
        '--verbose', dest='verbose', action='store_true', help='Pass verbose to see full output.'
    )
    parser.add_argument(
        '--terse',
        dest='verbose',
        action='store_false',
        help='Pass terse to see output of only one line per test (this is the default).',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    settings = ExperimentSettings(args.experiment)
    print('Testing experiment', settings.path)
    settings.path = os.path.join('..', settings.path)

    if args.test:
        scenario_files = [args.test]
    else:
        scenario_files = os.listdir(TESTS_DIR)
        if not scenario_files:
            print('No scenarios found in', settings.path)
            sys.exit()
    scenario_files = [os.path.join(TESTS_DIR, scenario_file) for scenario_file in scenario_files]

    DeepCow.restore_state(settings)
    CreatureClass = CREATURES[args.creature]
    creature = CreatureClass(0, 0, 0, 0)

    correct = 0
    for scenario_file in sorted(scenario_files):
        correct += run_scenario(scenario_file, creature, args.verbose, 1000)

    if len(scenario_files) > 1:
        percentage = 100 * correct / len(scenario_files)
        print(f'{correct:.0f}/{len(scenario_files)} passed ({percentage:.0f}%)')