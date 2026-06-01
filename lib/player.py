from lib.entity import *
from lib.bullet import *

from pplay.sprite import *
from pplay.collision import *

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
        # STATUS
        # =========================

        self.life = 3

        self.speed = 500

        self.direction = "right"

        # =========================
        # DANO
        # =========================

        self.invulnerable = False

        self.invulnerable_timer = 0

        self.invulnerable_duration = 1.0

        self.hit_timer = 0

        self.hit_duration = 0.3

        # =========================
        # LIMITES
        # =========================

        self.limite = Sprite(
            "sprites/wallpaper/level/limit.png"
        )

        self.jumping = False
        self.jump_cooldown = 0.3
        self.jump_timer = 0
        self.jump_duration = 0.5
        # =========================
        # TIROS
        # =========================

        self.bullets = []

        self.shoot_timer = 0

        self.shoot_cooldown = 0.3

        # =========================
        # ANIMAÇÕES
        # =========================

        self.idle_right_frames = [
            Sprite(
                f"sprites/player/idle_right/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/idle_right"
                )
            )
            if img.endswith(".png")
        ]

        self.idle_left_frames = [
            Sprite(
                f"sprites/player/idle_left/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/idle_left"
                )
            )
            if img.endswith(".png")
        ]

        self.walk_right_frames = [
            Sprite(
                f"sprites/player/walk_right/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/walk_right"
                )
            )
            if img.endswith(".png")
        ]

        self.walk_left_frames = [
            Sprite(
                f"sprites/player/walk_left/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/walk_left"
                )
            )
            if img.endswith(".png")
        ]

        self.walk_up_frames = [
            Sprite(
                f"sprites/player/walk_up/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/walk_up"
                )
            )
            if img.endswith(".png")
        ]

        self.walk_down_frames = [
            Sprite(
                f"sprites/player/walk_down/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/walk_down"
                )
            )
            if img.endswith(".png")
        ]

        self.hit_frames = [
            Sprite(
                f"sprites/player/hit/{img}"
            )
            for img in sorted(
                listdir(
                    "sprites/player/hit"
                )
            )
            if img.endswith(".png")
        ]

        self.current_animation = (
            self.idle_right_frames
        )

        self.frame = 0

        self.animation_timer = 0

        self.animation_speed = 0.12

    # ====================================
    # ANIMAÇÃO
    # ====================================

    def animate(self, dt):

        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:

            self.animation_timer = 0

            self.frame += 1

            if self.frame >= len(
                self.current_animation
            ):
                self.frame = 0

            old_x = self.sprite.x
            old_y = self.sprite.y

            self.sprite = (
                self.current_animation[
                    self.frame
                ]
            )

            self.sprite.x = old_x
            self.sprite.y = old_y

    # ====================================
    # DANO
    # ====================================

    def take_damage(self, damage):

        if self.invulnerable:
            return

        self.life -= damage

        self.invulnerable = True

        self.invulnerable_timer = (
            self.invulnerable_duration
        )

        self.hit_timer = (
            self.hit_duration
        )

    # ====================================
    # TIROS
    # ====================================

    def shoot(self, window):

        bullet = Bullet(

            window,

            self.sprite.x,

            self.sprite.y
            + self.sprite.height / 2,

            self.direction
        )

        self.bullets.append(
            bullet
        )

    # ====================================
    # UPDATE
    # ====================================

    def update(
        self,
        window,
        keyboard,
        dt
    ):

        moving = False

        # --------------------
        # MOVIMENTO
        # --------------------
        if self.jump_timer > 0:
            self.jump_timer -= dt

        if keyboard.key_pressed("SPACE"):
            self.jump()

        elif keyboard.key_pressed("A") or keyboard.key_pressed("LEFT"):

            self.sprite.x -= (
                self.speed * dt
            )

            self.direction = "left"

            moving = True

        elif keyboard.key_pressed("D") or keyboard.key_pressed("RIGHT"):

            self.sprite.x += (
                self.speed * dt
            )

            self.direction = "right"

            moving = True

        elif (
            keyboard.key_pressed("W")
            or keyboard.key_pressed("UP")
        ) and not Collision.collided(
            self.sprite,
            self.limite
        ):

            self.sprite.y -= (
                self.speed * dt
            )

            self.direction = "up"

            moving = True

        elif keyboard.key_pressed("S") or keyboard.key_pressed("DOWN"):

            self.sprite.y += (
                self.speed * dt
            )

            self.direction = "down"

            moving = True

        # --------------------
        # LIMITES DA TELA
        # --------------------

        self.sprite.x = max(
            0,
            min(
                self.sprite.x,
                window.width
                - self.sprite.width
            )
        )

        self.sprite.y = max(
            0,
            min(
                self.sprite.y,
                window.height
                - self.sprite.height
            )
        )

        # --------------------
        # HIT
        # --------------------

        if self.hit_timer > 0:

            self.hit_timer -= dt

            self.current_animation = (
                self.hit_frames
            )

        else:

            if self.direction == "right":

                if moving:

                    self.current_animation = (
                        self.walk_right_frames
                    )

                else:

                    self.current_animation = (
                        self.idle_right_frames
                    )

            elif self.direction == "left":

                if moving:

                    self.current_animation = (
                        self.walk_left_frames
                    )

                else:

                    self.current_animation = (
                        self.idle_left_frames
                    )

            elif self.direction == "up":

                if moving:

                    self.current_animation = (
                        self.walk_up_frames
                    )

                else:

                    self.current_animation = (
                        self.idle_right_frames
                    )

            elif self.direction == "down":

                if moving:

                    self.current_animation = (
                        self.walk_down_frames
                    )

                else:

                    self.current_animation = (
                        self.idle_right_frames
                    )

        # --------------------
        # TIROS
        # --------------------

        self.shoot_timer -= dt

        if (
            (
                keyboard.key_pressed("ENTER")
                or keyboard.key_pressed("Z")
            )
            and self.shoot_timer <= 0
        ):

            self.shoot(window)

            self.shoot_timer = (
                self.shoot_cooldown
            )

        # --------------------
        # UPDATE TIROS
        # --------------------

        for bullet in self.bullets[:]:

            bullet.update(dt)

            if (
                bullet.sprite.x < -100
                or bullet.sprite.x >
                window.width + 100
            ):

                self.bullets.remove(
                    bullet
                )

        # --------------------
        # INVULNERABILIDADE
        # --------------------

        if self.invulnerable:

            self.invulnerable_timer -= dt

            if (
                self.invulnerable_timer
                <= 0
            ):

                self.invulnerable = False

        # --------------------
        # ANIMAÇÃO
        # --------------------

        self.animate(dt)

    # ====================================
    # DRAW
    # ====================================

    def draw(self):

        self.sprite.draw()

        for bullet in self.bullets:

            bullet.draw()

    def jump(self):

        if self.jump_timer > 0:
            return

        if self.sprite.y > 500:

            self.sprite.y = 250

        else:

            self.sprite.y = 650

        self.jump_timer = self.jump_cooldown
