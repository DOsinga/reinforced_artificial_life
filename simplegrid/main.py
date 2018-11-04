#!/usr/bin/env python
import pygame

from shared.display import Display
from simplegrid.dqn_agent import DQNAgent
from simplegrid.world import World

FRAME_RATE = 60
TITLE = 'Reinforced Artificial Life'
EPISODES = 1000
BATCH_SIZE = 32


def update_screen(display, world, clock, life_expectancy):
    # --- Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return -1
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
    display.clear()
    world.draw(display)
    clock.tick(FRAME_RATE)
    display.flip()

    msg = TITLE + ' ' + world.get_info()
    if life_expectancy:
        avg = sum(life_expectancy) / len(life_expectancy)
        msg += ' ' + str(avg)
    pygame.display.set_caption(msg)


def main():
    display = Display(TITLE, 640, 480)
    clock = pygame.time.Clock()

    life_expectancy = []

    agent = DQNAgent(9, 4)
    for episode in range(EPISODES):
        world = World(20, 0.10)

        # Start with a random move:
        state, reward, _, _ = world.move(0)

        for tick in range(500):
            prev_state = state

            action = agent.act(state)
            state, reward, done, _ = world.move(action)

            if done:
                # Dying is bad:
                reward = -10

            agent.remember(prev_state, action, reward, state, done)

            if update_screen(display, world, clock, life_expectancy) == -1:
                return

            if done:
                break
        life_expectancy = life_expectancy[-4:] + [tick]

        if len(agent.memory) > BATCH_SIZE:
            agent.replay(BATCH_SIZE)



if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        pygame.quit()
