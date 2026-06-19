from lib.entity import *
from lib.bullet import *

from pplay.sprite import *
from pplay.collision import *

from os import listdir


class Player(Entity):
    mode = 1

    def __init__(self, window):
        super().__init__(
            "sprites/player/idle_right/idle_1.png",
            window,
            700,
            550    # spawn no chao
        )

        self.window = window
        self.life = 3
        self.speed = 500
        self.direction = "right"
        self.dt = 1 / 60

        # dano
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0
        self.hit_timer = 0
        self.hit_duration = 0.3

        # Y do chao — jogador pousa e anda aqui
        self.FLOOR_Y = 550

        # pulo fisico
        self.vel_y = 0.0
        self.gravity = 2200.0
        self.jump_force = -1100.0
        self.is_on_ground = True
        self.jump_pressed_last = False

        # tiros
        self.bullets = []
        self.shoot_timer = 0
        self.shoot_cooldown = 0.3*Player.mode

        # animações
        self.jump_frames = self._load_frames("sprites/player/jump")
        self.idle_right_frames = self._load_frames("sprites/player/idle_right")
        self.idle_left_frames = self._load_frames("sprites/player/idle_left")
        self.walk_right_frames = self._load_frames("sprites/player/walk_right")
        self.walk_left_frames = self._load_frames("sprites/player/walk_left")
        self.walk_up_frames = self._load_frames("sprites/player/walk_up")
        self.walk_down_frames = self._load_frames("sprites/player/walk_down")
        self.hit_frames = self._load_frames("sprites/player/hit")
        self.death_frames = self._load_frames("sprites/player/death")

        if not self.jump_frames:
            self.jump_frames = self.walk_up_frames

        self.current_animation = self.idle_right_frames
        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        self.dead = False
        self.death_timer = 0

    def _load_frames(self, path):
        try:
            files = sorted(f for f in listdir(path) if f.endswith(".png"))
            return [Sprite(f"{path}/{f}") for f in files]
        except FileNotFoundError:
            return []

    # ANIMACAO

    def animate(self, dt):
        self.dt = dt
        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame += 1

            if self.dead:
                if self.frame >= len(self.current_animation):
                    self.frame = len(self.current_animation) - 1
            else:
                if self.frame >= len(self.current_animation):
                    self.frame = 0

            old_x = self.sprite.x
            old_y = self.sprite.y
            self.sprite = self.current_animation[self.frame]
            self.sprite.x = old_x
            self.sprite.y = old_y

    # DANO

    def take_damage(self, damage):
        if self.invulnerable or self.dead:
            return

        self.life -= damage
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration
        self.hit_timer = self.hit_duration

        if self.life <= 0:
            self.life = 0
            self.dead = True
            self.sprite.y = self.FLOOR_Y
            self.death_timer = 2
            self.frame = 0
            self.current_animation = self.death_frames
            self.animate(self.dt)

    # TIROS

    def shoot(self, window):
        bullet = Bullet(
            window,
            self.sprite.x,
            self.sprite.y + self.sprite.height / 2,
            self.direction
        )
        self.bullets.append(bullet)

    # UPDATE

    def update(self, keyboard, dt):

        if self.dead:
            self.death_timer -= dt
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        moving = False

        # movimento horizontal
        if keyboard.key_pressed("A") or keyboard.key_pressed("LEFT"):
            self.sprite.x -= self.speed * dt
            self.direction = "left"
            moving = True

        elif keyboard.key_pressed("D") or keyboard.key_pressed("RIGHT"):
            self.sprite.x += self.speed * dt
            self.direction = "right"
            moving = True

        # pulo com SPACE — disparo unico por pressao
        jump_pressed = keyboard.key_pressed("SPACE")

        if jump_pressed and not self.jump_pressed_last:
            if self.is_on_ground:
                self.vel_y = self.jump_force
                self.is_on_ground = False
                self.frame = 0

        self.jump_pressed_last = jump_pressed

        # fisica vertical
        if not self.is_on_ground:
            self.vel_y += self.gravity * dt
            self.sprite.y += self.vel_y * dt

            if self.sprite.y >= self.FLOOR_Y:
                self.sprite.y = self.FLOOR_Y
                self.vel_y = 0.0
                self.is_on_ground = True

        # limites horizontais da tela
        self.sprite.x = max(0, min(self.sprite.x,
                                   self.window.width - self.sprite.width))

        # limites verticais da tela (seguranca)
        self.sprite.y = max(0, min(self.sprite.y,
                                   self.window.height - self.sprite.height))

        # selecao de animacao
        if self.hit_timer > 0:
            self.hit_timer -= dt
            self.current_animation = self.hit_frames

        elif not self.is_on_ground:
            self.current_animation = self.jump_frames

        else:
            if self.direction == "right":
                self.current_animation = (
                    self.walk_right_frames if moving else self.idle_right_frames
                )
            elif self.direction == "left":
                self.current_animation = (
                    self.walk_left_frames if moving else self.idle_left_frames
                )
            else:
                self.current_animation = self.idle_right_frames

        # tiros
        self.shoot_timer -= dt
        if (
            (keyboard.key_pressed("ENTER") or keyboard.key_pressed("Z"))
            and self.shoot_timer <= 0
        ):
            self.shoot(self.window)
            self.shoot_timer = self.shoot_cooldown

        for bullet in self.bullets[:]:
            bullet.update(dt)
            if bullet.sprite.x < -100 or bullet.sprite.x > self.window.width + 100:
                self.bullets.remove(bullet)

        # invulnerabilidade
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        self.animate(dt)

    # DRAW

    def draw(self):
        self.sprite.draw()
        for bullet in self.bullets:
            bullet.draw()
