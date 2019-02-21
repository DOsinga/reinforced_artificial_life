#!/usr/bin/env python
import argparse
import itertools
import time
import contextlib

from shared.display import Display
from shared.experiment_settings import ExperimentSettings
from simplegrid.deep_cow import DeepCow
from simplegrid.world import World as World
from shared.episode import Episode

TITLE = 'Reinforced Artificial Life'


def update_display(display, world):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return

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
    display.clear()
    world.update_sidebar(display)
    world.draw(display)
    display.flip()
    pygame.display.set_caption(TITLE + ' ' + world.get_info())


def main(settings, show_weights):

    display = None
    if not settings.display_off:
        display = Display(TITLE, settings.world_size, settings.scale)

    world = World(settings, display)

    for episode_count in itertools.count():
        # Play an episode
        episode = Episode()
        if display:
            display.sidebar['episode'] = episode_count

        world.reset(episode)
        steps = 0
        start_time = time.time()
        while True:
            steps += 1
            if not world.step():
                break
            if not settings.display_off:
                update_display(display, world)
        world.end(show_weights=show_weights)
        print(round(steps / (time.time() - start_time), 1), 'steps/second')


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
    settings = ExperimentSettings(args.experiment)
    if not settings.display_off:
        with contextlib.redirect_stdout(None):  # Suppress Hello from Pygame community message
            import pygame
        pygame.init()
    try:
        main(settings, args.show_weights)
    finally:
        if not settings.display_off:
            pygame.quit()
