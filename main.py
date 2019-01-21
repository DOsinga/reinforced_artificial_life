#!/usr/bin/env python
import argparse
import itertools

import contextlib

with contextlib.redirect_stdout(None):  # Suppress Hello from Pygame community message
    import pygame

from shared.display import Display
from shared.experiment_settings import ExperimentSettings
from simplegrid.deep_cow import DeepCow
from simplegrid.world import World as World
from shared.episode import Episode

FRAME_RATE = 60
TITLE = 'Reinforced Artificial Life'


def main(settings):

    display = Display(TITLE, settings.world_size, settings.scale)
    clock = pygame.time.Clock()

    world = World(settings, display)

    for episode_count in itertools.count( 1 ):
        # Play an episode
        episode = Episode()
        display.sidebar['episode'] = episode_count

        world.reset(episode)
        while True:
            # --- Event Processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        display.reset_offsets()

            keys_down = pygame.key.get_pressed()
            if keys_down[pygame.K_LEFT]:
                display.offset_x += 10
            elif keys_down[pygame.K_RIGHT]:
                display.offset_x -= 10
            elif keys_down[pygame.K_UP]:
                display.offset_y += 10
            elif keys_down[pygame.K_DOWN]:
                display.offset_y -= 10
            elif keys_down[pygame.K_a]:
                display.scale *= 1.05
            elif keys_down[pygame.K_z]:
                display.scale /= 1.05
            elif keys_down[pygame.K_d]:
                print(DeepCow.agent.identity_test())
            else:
                if not world.step():
                    break
            display.clear()
            world.draw(display)
            clock.tick(FRAME_RATE)
            display.flip()
            pygame.display.set_caption(TITLE + ' ' + world.get_info())
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
    parser.add_argument(
        '--showweights',
        required=False,
        dest='show_weights',
        action='store_true',
        help='Shows network weights after each generation.',
    )
    args = parser.parse_args()
    settings = ExperimentSettings(args.experiment, args.show_weights)
    pygame.init()
    try:
        main(settings)
    finally:
        pygame.quit()
