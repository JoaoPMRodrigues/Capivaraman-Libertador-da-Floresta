from lib.boss import *
from pplay.sprite import *
from random import randint
from os import listdir

from lib.tornado import *


class Saci(Boss):

    def __init__(self, window):

        super().__init__(
            "sprites/boss/saci/idle_right/saci_idle1.png",
            window,
            1150,
            500,
            100
        )

        # ==========================
        # POSIÇÕES DA ARENA
        # ==========================

        self.positions = [

            (1150, 500),  # chão direito

            (1150, 50),  # plataforma direita

            (250, 500)    # chão esquerdo
        ]

        self.current_position = 0

        # ==========================
        # ANIMAÇÕES
        # ==========================

        self.idle_frames = [
            Sprite(
                f"sprites/boss/saci/idle_right/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/boss/saci/idle_right"
                )
            )
        ]

        self.attack_frames = [
            Sprite(
                f"sprites/boss/saci/attack/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/boss/saci/attack"
                )
            )
        ]

        self.hit_frames = [
            Sprite(
                f"sprites/boss/saci/hit/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/boss/saci/hit"
                )
            )
        ]

        self.death_frames = [
            Sprite(
                f"sprites/boss/saci/death/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/boss/saci/death"
                )
            )
        ]

        self.frame = 0

        self.animation_timer = 0

        self.animation_speed = 0.15

        self.current_animation = self.idle_frames

        self.tornados = []

        self.attack_timer = 0

        self.attack_cooldown = 2

        self.teleport_timer = 0

        self.teleport_cooldown = 3

        self.dashing = False

        self.dash_speed = 1500

        self.direction = "left"

        self.hit_timer = 0

        self.hit_duration = 0.2

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

    def teleport(self):

        if self.hp > 50:

            new_position = randint(0, 1)

        else:

            new_position = randint(0, 2)

        while new_position == self.current_position:

            if self.hp > 50:
                new_position = randint(0, 1)
            else:
                new_position = randint(0, 2)

        self.current_position = new_position

        self.sprite.x = self.positions[new_position][0]
        self.sprite.y = self.positions[new_position][1]

        if new_position == 2:

            self.direction = "right"

        else:

            self.direction = "left"

    def throw_tornado(self):

        tornado = Tornado(

            self.sprite.x,

            self.sprite.y +
            self.sprite.height / 2,

            self.direction
        )

        self.tornados.append(tornado)

    def dash(self):

        self.dashing = True

        self.state = "dash"

    def update_dash(self, dt, player):

        if not self.dashing:
            return

        self.sprite.x -= self.dash_speed * dt

        if self.sprite.collided(player.sprite):

            player.take_damage(1)

        if self.sprite.x <= 250:

            self.sprite.x = 250

            self.dashing = False

            self.state = "idle"

    def check_bullets(self, player):

        for bullet in player.bullets[:]:

            if self.sprite.collided(
                bullet.sprite
            ):

                self.take_damage(1)

                self.hit_timer = self.hit_duration

                player.bullets.remove(
                    bullet
                )

    def update(self, dt, player):

        if self.dead:

            self.current_animation = (
                self.death_frames
            )

            self.animate(dt)

            return

        # -----------------------

        self.attack_timer += dt

        self.teleport_timer += dt

        # -----------------------

        if self.hp <= 50:

            if (
                not self.dashing
                and randint(0, 400) == 0
            ):
                self.dash()

        # -----------------------

        if (
            self.teleport_timer
            >= self.teleport_cooldown
        ):

            self.teleport()

            self.teleport_timer = 0

        # -----------------------

        if (
            self.attack_timer
            >= self.attack_cooldown
        ):

            self.throw_tornado()

            self.attack_timer = 0

        # -----------------------

        self.update_dash(dt, player)
        self.check_bullets(player)

        # -----------------------

        if self.hit_timer > 0:

            self.hit_timer -= dt

            self.state = "hit"

        else:

            if not self.dashing:

                self.state = "idle"

        if self.state == "hit":

            self.current_animation = (
                self.hit_frames
            )

        elif self.state == "death":

            self.current_animation = (
                self.death_frames
            )

        else:

            self.current_animation = (
                self.idle_frames
            )

        self.animate(dt)

        for tornado in self.tornados[:]:

            tornado.update(dt)

            if tornado.sprite.collided(
                player.sprite
            ):

                player.take_damage(1)

                self.tornados.remove(
                    tornado
                )

            elif (
                tornado.sprite.x < -200
                or tornado.sprite.x >
                self.sprite.x + 2000
            ):

                self.tornados.remove(
                    tornado
                )

    def draw(self):

        self.sprite.draw()

        for tornado in self.tornados:

            tornado.draw()
