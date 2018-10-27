import pygame


class Display():
    def __init__(self, title, width, height, delay=30):
        self.width = width
        self.height = height
        self.reset_offsets()

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.delay = delay

    def reset_offsets(self):
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def clear(self):
        self.screen.fill((0, 0, 0))

    def circle(self, color, x, y, radius):
        x = int(x * self.scale - self.offset_x + self.width / 2)
        y = int(y * self.scale - self.offset_y + self.height / 2)
        pygame.draw.circle(self.screen, color, (x, y), int(radius * self.scale))

    def flip(self):
        pygame.display.flip()
