import pygame


class Display:
    def __init__(self, title, world_size, initial_scale, delay=30):
        self.width = world_size * initial_scale
        self.height = world_size * initial_scale
        self.world_size = world_size
        self.initial_scale = initial_scale
        self.reset_offsets()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
        self.delay = delay

    def reset_offsets(self):
        self.scale = self.initial_scale
        self.offset_x = 0
        self.offset_y = 0

    def clear(self):
        self.screen.fill((0, 0, 0))

    def circle(self, x, y, radius, color):
        x, y = self.to_display_coords(x, y)
        pygame.draw.circle(self.screen, color, (x, y), int(radius * self.scale))

    def to_display_coords(self, x, y):
        if x == 2 and y == 2:
            x = 2
        x1 = int(self.offset_x + self.width / 2 + self.scale * (x + 0.5 - self.world_size / 2))
        y1 = int(self.offset_y + self.height / 2 + self.scale * (y + 0.5 - self.world_size / 2))
        return x1, y1
        # x = int(x * self.scale - self.offset_x + self.width / 2)
        # y = int(y * self.scale - self.offset_y + self.height / 2)
        # return x, y

    # def dot(self, color, x, y):
    #     if self.scale < 0.5:
    #         return
    #     x, y = self.to_display_coords(x, y)
    #     if self.scale > 2.0:
    #         pygame.draw.circle(self.screen, color, (x, y), int(self.scale / 2))
    #     else:
    #         if self.scale < 1.0:
    #             f = (self.scale - 0.5) / 0.5
    #             color = tuple(map(lambda c: int(c * f), color))
    #         self.screen.set_at((x, y), color)

    def rectangle(self, x, y, size, color):
        x1, y1 = self.to_display_coords(x - 0.4, y - 0.4)
        x2, y2 = self.to_display_coords(x + 0.4, y + 0.4)
        w = x2 - x1
        h = y2 - y1
        pygame.draw.rect(self.screen, color, (x1, y1, w, h), 0)

    def flip(self):
        pygame.display.flip()
