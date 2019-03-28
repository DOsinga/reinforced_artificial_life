import pygame
from collections import OrderedDict

sidebar_width = 200
FRAME_RATE = 60


class Display:
    def __init__(self, title, world_size, initial_scale, delay=30):
        self.active = False
        self.clock = pygame.time.Clock()
        self.width = world_size * initial_scale
        self.height = world_size * initial_scale
        self.world_size = world_size
        self.initial_scale = initial_scale
        self.reset_offsets()

        self.screen = pygame.display.set_mode((self.width + sidebar_width, self.height))
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont('Arial', 11)
        self.sidebar = OrderedDict()
        self.delay = delay

    def reset_offsets(self):
        self.scale = self.initial_scale
        self.offset_x = 0
        self.offset_y = 0

    def clear(self):
        if not self.active:
            return
        self.screen.fill((0, 0, 0))

    def circle(self, x, y, radius, color):
        if not self.active:
            return
        x, y = self.to_display_coords(x + 0.5, y + 0.5)
        pygame.draw.circle(self.screen, color, (x, y), int(radius * self.scale))

    def to_display_coords(self, x, y):
        x1 = int(self.offset_x + self.width / 2 + self.scale * (x - self.world_size / 2))
        y1 = int(self.offset_y + self.height / 2 + self.scale * (y - self.world_size / 2))
        return x1, y1

    def rectangle(self, x, y, size, color, padding=0):
        if not self.active:
            return
        x1, y1 = self.to_display_coords(x + padding, y + padding)
        x2, y2 = self.to_display_coords(x + size - padding, y + size - padding)
        w = x2 - x1
        h = y2 - y1
        pygame.draw.rect(self.screen, color, (x1, y1, w, h), 0)

    def flip(self):
        if not self.active:
            return
        self.clock.tick(FRAME_RATE)
        self.draw_sidebar()
        pygame.display.flip()

    def draw_text(self, x, y, text):
        if not self.active:
            return
        rendered = self.font.render(text, True, pygame.Color("white"))
        self.screen.blit(rendered, (x + self.width, y))

    def draw_sidebar(self):
        if not self.active:
            return
        y = 10
        for key, val in self.sidebar.items():
            self.draw_text(10, y, key)
            self.draw_text(130, y, str(val))
            y += 30
