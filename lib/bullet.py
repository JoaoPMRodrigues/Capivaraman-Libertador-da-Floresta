from lib.entity import *


class Bullet(Entity):

    def __init__(self, window, x, y, direction):

        super().__init__(
            "sprites/bullet/bullet.png",
            window,
            x,
            y
        )
        self.direction = direction
        self.speed = 1000

    def update(self, dt):
        if self.direction == "right":
            self.sprite.x += self.speed * dt
        else:
            self.sprite.x -= self.speed * dt
