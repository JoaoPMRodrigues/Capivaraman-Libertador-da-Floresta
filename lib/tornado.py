from pplay.sprite import *


class Tornado:

    def __init__(self, x, y, direction):

        self.sprite = Sprite(
            "sprites/boss/saci/tornado/tornado1.png"
        )

        self.sprite.x = x
        self.sprite.y = y

        self.direction = direction

        self.speed = 700

    def update(self, dt):

        if self.direction == "left":

            self.sprite.x -= self.speed * dt

        else:

            self.sprite.x += self.speed * dt

    def draw(self):

        self.sprite.draw()
