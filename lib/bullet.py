from lib.entity import *


class Bullet(Entity):

    def __init__(self, window, x, y):

        super().__init__(
            "sprites/bullet/bullet.png",
            window,
            x,
            y
        )

        self.speed = 1000

    def update(self, dt):

        self.sprite.x += self.speed * dt
