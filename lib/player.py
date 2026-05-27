from lib.entity import *
from pplay.keyboard import *
from pplay.sprite import *
import os


class Player(Entity):

    def __init__(self, window):

        super().__init__(
            "sprites/player/idle/idle_0.png",
            window,
            700,
            500
        )

        self.speed = 500

        self.idle_frames = [
            Sprite(f"sprites/player/idle/{img}")
            for img in sorted(os.listdir("sprites/player/idle"))
        ]

        self.walk_right_frames = [
            Sprite(f"sprites/player/walk_right/{img}")
            for img in sorted(os.listdir("sprites/player/walk_right"))
        ]

        self.walk_left_frames = [Sprite(f"sprites/player/malk_left")
                                 for img in sorted(os.listdir("sprites/player/malk_left"))]

        self.current_animation = self.idle_frames

        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12

    def animate(self, dt):

        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:

            self.animation_timer = 0

            self.frame += 1

            if self.frame >= len(self.current_animation):
                self.frame = 0

            old_x = self.sprite.x
            old_y = self.sprite.y

            self.sprite = self.current_animation[self.frame]

            self.sprite.x = old_x
            self.sprite.y = old_y

    def update(self, window, keyboard, dt):

        moving_right = moving_left = False

        if keyboard.key_pressed("A"):
            self.sprite.x -= self.speed * dt
            moving_left = True

        if keyboard.key_pressed("D"):
            self.sprite.x += self.speed * dt
            moving_right = True

        if keyboard.key_pressed("W"):
            self.sprite.y -= self.speed * dt
            moving = True

        if keyboard.key_pressed("S"):
            self.sprite.y += self.speed * dt
            moving = True

        # Troca animação

        if moving_right:
            self.current_animation = self.walk_right_frames
        elif moving_left:
            self.current_animation = self.walk_left_frames
        else:
            self.current_animation = self.idle_frames

        self.animate(dt)
