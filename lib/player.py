from lib.entity import *
from lib.bullet import *

from pplay.keyboard import *
from pplay.sprite import *

from os import listdir


class Player(Entity):

    def __init__(self, window):

        super().__init__(
            "sprites/player/idle_right/idle_1.png",
            window,
            700,
            500
        )

        # =========================
        # MOVIMENTO
        # =========================

        self.speed = 500

        self.direction = "right"

        # =========================
        # ANIMAÇÕES
        # =========================

        self.idle_right_frames = [
            Sprite(f"sprites/player/idle_right/{img}")
            for img in sorted(
                listdir("sprites/player/idle_right")
            )
        ]

        self.idle_left_frames = [
            Sprite(f"sprites/player/idle_left/{img}")
            for img in sorted(
                listdir("sprites/player/idle_left")
            )
        ]

        self.walk_right_frames = [
            Sprite(f"sprites/player/walk_right/{img}")
            for img in sorted(
                listdir("sprites/player/walk_right")
            )
        ]

        self.walk_left_frames = [
            Sprite(f"sprites/player/walk_left/{img}")
            for img in sorted(
                listdir("sprites/player/walk_left")
            )
        ]

        self.current_animation = (
            self.idle_right_frames
        )

        self.frame = 0

        self.animation_timer = 0

        self.animation_speed = 0.12

        self.bullets = []

        self.shoot_timer = 0

        self.shoot_cooldown = 0.3

    def animate(self, dt):

        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:

            self.animation_timer = 0

            self.frame += 1

            if self.frame >= len(self.current_animation):
                self.frame = 0

            old_x = self.sprite.x
            old_y = self.sprite.y

            self.sprite = (
                self.current_animation[self.frame]
            )

            self.sprite.x = old_x
            self.sprite.y = old_y

    def update(self, window, keyboard, dt):

        moving = False

        if keyboard.key_pressed("A") or keyboard.key_pressed("LEFT"):

            self.sprite.x -= self.speed * dt

            self.direction = "left"

            moving = True

            if self.sprite.x < 0:
                self.sprite.x = 0

        if keyboard.key_pressed("D") or keyboard.key_pressed("RIGHT"):

            self.sprite.x += self.speed * dt

            self.direction = "right"

            moving = True

            if self.sprite.x + self.sprite.width > window.width:
                self.sprite.x = (
                    window.width - self.sprite.width
                )

        if keyboard.key_pressed("W") or keyboard.key_pressed("UP"):

            self.sprite.y -= self.speed * dt

            moving = True

            if self.sprite.y < 0:
                self.sprite.y = 0

        if keyboard.key_pressed("S") or keyboard.key_pressed("DOWN"):

            self.sprite.y += self.speed * dt

            moving = True

            if self.sprite.y + self.sprite.height > window.height:
                self.sprite.y = (
                    window.height - self.sprite.height
                )

        if self.direction == "right":

            if moving:
                self.current_animation = (
                    self.walk_right_frames
                )
            else:
                self.current_animation = (
                    self.idle_right_frames
                )

        else:

            if moving:
                self.current_animation = (
                    self.walk_left_frames
                )
            else:
                self.current_animation = (
                    self.idle_left_frames
                )

        self.animate(dt)

        self.shoot_timer -= dt

        if (keyboard.key_pressed("SPACE") and self.shoot_timer <= 0):

            bullet = Bullet(
                window,
                self.sprite.x,
                self.sprite.y
                + self.sprite.height / 2,
                self.direction
            )

            self.bullets.append(bullet)

            self.shoot_timer = (
                self.shoot_cooldown
            )

        for bullet in self.bullets[:]:

            bullet.update(dt)

            if (
                bullet.sprite.x < -100
                or bullet.sprite.x > window.width + 100
            ):
                self.bullets.remove(bullet)

    def draw(self):

        self.sprite.draw()

        for bullet in self.bullets:
            bullet.draw()
