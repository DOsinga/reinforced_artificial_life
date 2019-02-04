import argparse
import random
import numpy as np
import itertools

from simplegrid.deep_cow import DeepCow
from simplegrid.map_feature import MapFeature
from simplegrid.cow import Action
from shared.experiment_settings import ExperimentSettings
from simplegrid.world import World
from unittest.mock import MagicMock


def train_cow(settings):
    settings.world_size = 5
    settings.start_num_creatures = 0
    world = World(settings, MagicMock())
    world.reset(MagicMock())
    deepcow = DeepCow(x=2, y=2, settings=settings, energy=100)

    features = [MapFeature.EMPTY.index, MapFeature.GRASS.index, MapFeature.ROCK.index]
    training_data = np.asarray(list(itertools.product(features, repeat=12)))
    np.random.shuffle(training_data)
    print(len(training_data))

    directions_in_diamond = {Action.LEFT: 2, Action.UP: 5, Action.DOWN: 7, Action.RIGHT: 9}

    sum = hit = mis = 0
    for idx, diamond in enumerate(training_data):

        grass = MapFeature.GRASS.to_feature_vector(diamond)
        rock = MapFeature.ROCK.to_feature_vector(diamond)

        state = np.concatenate((grass, rock))

        action = deepcow.step(None, state)
        reward = -settings.move_cost / settings.grass_energy
        if diamond[directions_in_diamond[action]] == -1:  # grass
            reward += 1

        deepcow.learn(reward, False)

        sum += reward
        if reward > 0:
            hit += 1
        else:
            mis += 1

        if idx % 1000 == 999:
            print(
                f'{idx+1}, avg. reward: {sum / (idx+1):0.3f}, hitrate: {100*hit/(hit+mis):0.0f}%'
            )
            hit = mis = 0

    world.end()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--experiment',
        type=str,
        required=False,
        help='Specifies the experiment to run. This should be a directory '
        'where the specific settings and various state files are stored. Directory will '
        'be created and initialized if it does not exist.',
    )
    args = parser.parse_args()
    settings = ExperimentSettings(args.experiment)

    train_cow(settings)
