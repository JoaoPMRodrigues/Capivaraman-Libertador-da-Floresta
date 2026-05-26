# lib/player.py

from pplay.keyboard import *
from lib.entity import *


class Player(Entity):

    def __init__(self, window):

        super().__init__(
            "sprites/player/idle/idled1.png",
            window,
            700,
            500
        )

        self.speed = 500

    def update(self, window, keyboard, dt):

        if keyboard.key_pressed("A"):
            self.sprite.x -= self.speed * dt

        if keyboard.key_pressed("D"):
            self.sprite.x += self.speed * dt

        if keyboard.key_pressed("W"):
            self.sprite.y -= self.speed * dt

        if keyboard.key_pressed("S"):
            self.sprite.y += self.speed * dt

        # Limites da tela

        if self.sprite.x < 0:
            self.sprite.x = 0

        if self.sprite.y < 0:
            self.sprite.y = 0

        if self.sprite.x + self.sprite.width > window.width:
            self.sprite.x = window.width - self.sprite.width

        if self.sprite.y + self.sprite.height > window.height:
            self.sprite.y = window.height - self.sprite.height
