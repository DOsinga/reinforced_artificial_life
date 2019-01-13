#!/usr/bin/env python
import argparse

import pygame

from shared.display import Display
from ballworld.world import World as BallWorld
from simplegrid.world import World as GridWorld
from shared.episode import Episode
from pathlib import Path

WORLDS = {'ball': BallWorld, 'grid': GridWorld}

FRAME_RATE = 60
TITLE = 'Reinforced Artificial Life'
WORLD_SIZE = 60
SCALE = 10


def main(WorldClass):
    script_path = Path(__file__).resolve().parent
    state_pattern = script_path / 'state' / 'last_{filename}'

    display = Display(TITLE, WORLD_SIZE, SCALE)
    clock = pygame.time.Clock()

    world = WorldClass(WORLD_SIZE, display)

    while True:

        # Play an episode
        episode = Episode()

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
        world.end(state_pattern)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--world', type=str, choices=list(WORLDS), required=True)
    args = parser.parse_args()
    pygame.init()
    try:
        main(WORLDS[args.world])
    finally:
        pygame.quit()
