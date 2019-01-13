#!/usr/bin/env python
import argparse
import itertools

import pygame

from shared.display import Display
from ballworld.world import World as BallWorld
from shared.experiment_settings import ExperimentSettings
from simplegrid.world import World as GridWorld
from shared.episode import Episode

WORLDS = {'ball': BallWorld, 'grid': GridWorld}

FRAME_RATE = 60
TITLE = 'Reinforced Artificial Life'


def main(WorldClass, settings):

    display = Display(TITLE, settings.world_size, settings.scale)
    clock = pygame.time.Clock()

    world = WorldClass(settings, display)

    for episode_count in itertools.count():
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
    parser.add_argument('--world', type=str, choices=list(WORLDS), required=True)
    parser.add_argument(
        '--experiment',
        type=str,
        required=False,
        help='Optional argument specifying the experiment to run. This should be a directory '
        'where the specific settings and various state files are stored. Directoy will '
        'be created and initialized if it does not exist.',
    )
    args = parser.parse_args()
    settings = ExperimentSettings(args.experiment)
    pygame.init()
    try:
        main(WORLDS[args.world], settings)
    finally:
        pygame.quit()
