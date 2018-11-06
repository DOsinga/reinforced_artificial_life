#!/usr/bin/env python
import pygame

from display import Display
from world import World

FRAME_RATE = 30
TITLE = 'Reinforced Artificial Life'
WORLDSIZE = 31
ZOOM = 18


def main():
    world = World(WORLDSIZE)

    display = Display(TITLE, WORLDSIZE, WORLDSIZE, ZOOM)
    clock = pygame.time.Clock()

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
            world.step()
        world.draw(display)
        clock.tick(FRAME_RATE)
        display.flip()
        pygame.display.set_caption(TITLE + ' ' + world.get_info())


if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        pygame.quit()
