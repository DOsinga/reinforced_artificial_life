#!/usr/bin/env python
import argparse

import pygame

from shared.display import Display
from ballworld.world import World as BallWorld
from simplegrid.world import World as GridWorld

WORLDS = {'ball': BallWorld,
          'grid': GridWorld}

FRAME_RATE = 60
TITLE = 'Reinforced Artificial Life'


def main(WorldClass):
    display = Display(TITLE, 640, 480)
    clock = pygame.time.Clock()


    while True:
        world = WorldClass(100, display)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--world', type=str, choices=list(WORLDS), required=True)
    args = parser.parse_args()
    pygame.init()
    try:
        main(WORLDS[args.world])
    finally:
        pygame.quit()
