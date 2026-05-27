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

        self.speed = 500
        self.direction = "right"
        self.idle_right_frames = [
            Sprite(f"sprites/player/idle_right/{img}")
            for img in sorted(listdir("sprites/player/idle_right"))
        ]
        self.idle_left_frames = [
            Sprite(f"sprites/player/idle_left/{img}")
            for img in sorted(listdir("sprites/player/idle_left"))
        ]

        self.walk_right_frames = [
            Sprite(f"sprites/player/walk_right/{img}")
            for img in sorted(listdir("sprites/player/walk_right"))
        ]

        self.walk_left_frames = [Sprite(f"sprites/player/walk_left/{img}")
                                 for img in sorted(listdir("sprites/player/walk_left"))]

        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12

        self.bullets = []

        self.shoot_timer = 0.3
        self.shoot_cooldown = 0.3

    def animate(self, dt, shotting=False):

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


# Movimento horizontal

        if keyboard.key_pressed("A"):

            self.sprite.x -= self.speed * dt
            moving_left = True
            self.direction = "left"

            # Barreira esquerda
            if self.sprite.x < 0:
                self.sprite.x = 0

        if keyboard.key_pressed("D"):

            self.sprite.x += self.speed * dt
            moving_right = True
            self.direction = "right"

            # Barreira direita
            if self.sprite.x + self.sprite.width > window.width:
                self.sprite.x = window.width - self.sprite.width

        # Movimento vertical

        if keyboard.key_pressed("W"):

            self.sprite.y -= self.speed * dt

            # Barreira superior
            if self.sprite.y < 0:
                self.sprite.y = 0

        if keyboard.key_pressed("S"):

            self.sprite.y += self.speed * dt

            # Barreira inferior
            if self.sprite.y + self.sprite.height > window.height:
                self.sprite.y = window.height - self.sprite.height

        # Troca animação
        if self.direction == "right":
            if moving_right:
                self.current_animation = self.walk_right_frames
            else:
                self.current_animation = self.idle_right_frames
        else:
            if moving_left:
                self.current_animation = self.walk_left_frames
            else:
                self.current_animation = self.idle_left_frames

        self.animate(dt)

        if keyboard.key_pressed("SPACE") and self.shoot_cooldown < 0:
            bullet = Bullet(
                window,
                self.sprite.x,
                self.sprite.y + self.sprite.height / 2,
                self.direction
            )

            self.bullets.append(bullet)
            self.shoot_cooldown = self.shoot_timer

        for bullet in self.bullets:
            bullet.update(dt)
            bullet.draw()

            if bullet.sprite.x < 0 or bullet.sprite.x > window.width+bullet.sprite.x:
                self.bullets.remove(bullet)

        self.shoot_cooldown -= dt
