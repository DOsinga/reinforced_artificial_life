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

import time

TITLE = 'Reinforced Artificial Life'
SAMPLE_RATE_DISPLAY_NON_ACTIVE = 10


def main(settings, show_weights):
    display = Display(TITLE, settings.world_size, settings.scale)

    world = World(settings, display)

    last_frame = time.time()
    fps = 0

    for episode_count in itertools.count():
        # Play an episode
        episode = Episode()
        display.sidebar['episode'] = episode_count

        world.reset(episode)
        for step_count in itertools.count():
            # --- Event Processing
            if display.active or step_count % SAMPLE_RATE_DISPLAY_NON_ACTIVE == 0:
                display.clear()
                world.draw(display)
                display.flip()
                pygame.display.set_caption(f'{TITLE} {world.get_info()} fps:{fps:2.1f}')
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            display.reset_offsets()
                        elif event.key == pygame.K_SPACE:
                            display.active = not display.active

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
            if not world.step():
                break
            cur_fps = 1 / (time.time() - last_frame)
            last_frame = time.time()
            if not fps:
                fps = cur_fps
            else:
                fps = 0.9 * fps + cur_fps * 0.1
        world.end(show_weights=show_weights)


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
    pygame.init()
    try:
        main(settings, args.show_weights)
    finally:
        pygame.quit()
