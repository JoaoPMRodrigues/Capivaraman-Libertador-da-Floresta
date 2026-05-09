from pplay.sprite import *
from pplay.keyboard import *
from lib.entity import *


class Player(Entity):
    def __init__(self, path, window, x, y, speed):
        super().__init__(path, window, x, y)
        self.speed = speed
        self.cooldown = 0.5
        self.base = 0.5
        self.timer = 0

    def new_speed(self, speed):
        self.speed = speed

    def recarga(self, dificuldade):
        self.cooldown = self.base * dificuldade

    def update(self, window, keyboard, dt):
        # Movimento

        if self.timer > 0:
            self.timer -= dt/50

        if keyboard.key_pressed("LEFT"):
            self.sprite.x -= self.speed*dt
        if keyboard.key_pressed("RIGHT"):
            self.sprite.x += self.speed*dt
        # Colisão paredes
        if self.sprite.x < 0:
            self.sprite.x = 0
        if self.sprite.x + self.sprite.width > window.width:
            self.sprite.x = window.width - self.sprite.width
