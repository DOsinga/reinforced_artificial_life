GRASS_COLOR = (50, 200, 50)


class Grass:
    count = -1

    def __init__(self, x, y):
        self.id = Grass.count
        Grass.count -= 1
        self.x = x
        self.y = y

    def draw(self, display):
        display.rect( GRASS_COLOR, self.x, self.y )
        #display.dot(GRASS_COLOR, self.x, self.y)

    def box(self):
        return self.x, self.y, self.x, self.y

    def radius(self):
        return 1
