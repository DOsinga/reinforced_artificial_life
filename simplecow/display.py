import pygame


class Display:
    def __init__(self, title, width, height, zoom=8):
        self.width = width * zoom
        self.height = height * zoom

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
        self.zoom = zoom
        # self.delay = delay

    def clear(self):
        self.screen.fill((0, 0, 0))

    def circle(self, color, x, y, radius):
        x, y = self.to_display_coords(x, y)
        pygame.draw.circle(
            self.screen,
            color,
            (x + self.zoom // 2, y + self.zoom // 2),
            int(radius / 2 * self.zoom),
        )

    def rect(self, color, x, y):
        x, y = self.to_display_coords(x + 0.1, y + 0.1)
        w = h = int(0.8 * self.zoom)
        pygame.draw.rect(self.screen, color, (x, y, w, h), 0)

    def to_display_coords(self, x, y):
        return x * self.zoom, y * self.zoom
        # x = int(x  - self.width / 2)
        # y = int(y  - self.height / 2)
        # return x, y

    # def dot(self, color, x, y):
    #    x, y = self.to_display_coords(x, y)
    #    self.screen.set_at((x, y), color)

    def flip(self):
        pygame.display.flip()
