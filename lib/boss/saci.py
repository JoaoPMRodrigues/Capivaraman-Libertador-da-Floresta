from lib.boss.boss import *
from pplay.sprite import *
from random import randint
from os import listdir

from lib.boss.tornado import *

FLOOR_Y = 375


class Saci(Boss):

    def __init__(self, window):

        super().__init__(
            "sprites/boss/saci/idle_left/saci_idle1.png",
            window, 1650, FLOOR_Y, 100)

        self.window = window

        self._raw_positions = [
            (1650, FLOOR_Y),   # 0: direita
            (30,   FLOOR_Y),   # 1: esquerda
        ]
        self.positions = list(self._raw_positions)
        self.current_position = 0   # comeca na direita

        # animacoes
        self.idle_right_frames = self._load_frames(
            "sprites/boss/saci/idle_right")
        self.idle_left_frames = self._load_frames(
            "sprites/boss/saci/idle_left")
        self.attack_frames = self._load_frames("sprites/boss/saci/attack")
        self.hit_frames = self._load_frames("sprites/boss/saci/hit")
        self.death_frames = self._load_frames("sprites/boss/saci/death")

        self.dead = False
        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.4
        self.current_animation = self.idle_left_frames

        # combate
        self.tornados = []
        self.attack_timer = 0
        self.attack_cooldown = 2.7

        # dash
        self.dashing = False
        self.dash_speed = 1100
        self.dash_target = 0
        self.direction = "left"

        # cooldown do dash para nao ficar dasheando sem parar
        self.dash_timer = 0
        self.dash_cooldown = 3.0   # segundos entre dashes (fase 2)

        self.hit_timer = 0
        self.hit_duration = 0.2

        self._fix_positions()

    # =========================================================
    # HELPERS
    # =========================================================

    def _load_frames(self, path):
        files = sorted(f for f in listdir(path) if f.endswith(".png"))
        return [Sprite(f"{path}/{f}") for f in files]

    def _fix_positions(self):
        h = self.sprite.height
        w = self.sprite.width
        ww = self.window.width
        wh = self.window.height

        floor_y_clamped = max(0, min(FLOOR_Y, wh - h))

        self.positions = [
            (max(0, min(x, ww - w)), floor_y_clamped)
            for (x, _) in self._raw_positions
        ]

        self.sprite.x = self.positions[0][0]
        self.sprite.y = self.positions[0][1]

    # =========================================================
    # ANIMACAO
    # =========================================================

    def animate(self, dt):
        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame += 1

            if self.state == "death":
                if self.frame >= len(self.current_animation):
                    self.frame = len(self.current_animation) - 1
                return
            else:
                if self.frame >= len(self.current_animation):
                    self.frame = 0

            old_x = self.sprite.x
            old_y = self.sprite.y
            self.sprite = self.current_animation[self.frame]
            self.sprite.x = old_x
            self.sprite.y = old_y

    # =========================================================
    # ATAQUE: TORNADO
    # =========================================================

    def throw_tornado(self, player):
        player_feet_y = player.sprite.y + player.sprite.height

        launch_x = (self.sprite.x if self.direction == "left"
                    else self.sprite.x + self.sprite.width)

        tornado = Tornado(launch_x, player_feet_y, self.direction)
        self.tornados.append(tornado)

    # =========================================================
    # DASH
    # Unico meio de movimento do Saci.
    # Vai do lado atual para o oposto e fica la ate o proximo dash.
    # =========================================================

    def try_dash(self):
        if self.dashing:
            return

        self.dashing = True
        self.state = "dash"

        # destino: lado oposto
        if self.current_position == 0:   # direita -> esquerda
            self.dash_target = 1
            self.direction = "left"
        else:                             # esquerda -> direita
            self.dash_target = 0
            self.direction = "right"

    def update_dash(self, dt, player):
        if not self.dashing:
            return

        ww = self.window.width
        sw = self.sprite.width
        dest_x = self.positions[self.dash_target][0]
        dest_y = self.positions[self.dash_target][1]

        if self.direction == "right":
            self.sprite.x += self.dash_speed * dt
            arrived = self.sprite.x >= dest_x
        else:
            self.sprite.x -= self.dash_speed * dt
            arrived = self.sprite.x <= dest_x

        if arrived:
            self.sprite.x = dest_x
            self.sprite.y = dest_y
            self.current_position = self.dash_target
            self.dashing = False
            self.state = "idle"
            self.dash_timer = 0   # reinicia cooldown
            # olha para o centro da arena ao parar
            self.direction = "right" if self.current_position == 1 else "left"

        self.sprite.x = max(0, min(self.sprite.x, ww - sw))

        if self._dash_hits_player(player):
            player.take_damage(1)

    def _dash_hits_player(self, player) -> bool:
        if not self.sprite.collided(player.sprite):
            return False
        # pulo por cima evita dano
        saci_center_y = self.sprite.y + self.sprite.height / 2
        player_feet_y = player.sprite.y + player.sprite.height
        if player_feet_y < saci_center_y:
            return False
        return True

    # =========================================================
    # DANO
    # =========================================================

    def check_bullets(self, player):
        for bullet in player.bullets[:]:
            if self.sprite.collided(bullet.sprite):
                self.take_damage(1)
                self.hit_timer = self.hit_duration
                player.bullets.remove(bullet)
                continue

            for tornado in self.tornados[:]:
                if not tornado.dead and tornado.sprite.collided(bullet.sprite):
                    destroyed = tornado.take_hit()
                    player.bullets.remove(bullet)
                    if destroyed:
                        self.tornados.remove(tornado)
                    break

    def take_damage(self, damage):
        if self.dead:
            self.tornados.clear()
            return

        self.hp -= damage

        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.state = "death"
            self.frame = 0
            self.current_animation = self.death_frames

    # =========================================================
    # UPDATE
    # Sem teleporte — o Saci so se move por dash
    # =========================================================

    def update(self, dt, player):

        if self.dead:
            self.tornados.clear()
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        self.attack_timer += dt

        # dash com cooldown (fase 2: hp <= 50)
        if self.hp <= 65 and not self.dashing:
            self.dash_timer += dt
            if self.dash_timer >= self.dash_cooldown:
                # adiciona um pouco de aleatoriedade ao timing
                if randint(0, 1) == 0:
                    self.try_dash()
                else:
                    self.dash_timer = self.dash_cooldown - 0.5

        # ataque
        if self.attack_timer >= self.attack_cooldown:
            self.throw_tornado(player)
            self.attack_timer = 0

        self.update_dash(dt, player)
        self.check_bullets(player)

        # estado
        if self.hit_timer > 0:
            self.hit_timer -= dt
            self.state = "hit"
        else:
            if not self.dashing:
                self.state = "idle"

        # animacao
        if self.state == "hit":
            self.current_animation = self.hit_frames
        elif self.state == "death":
            self.current_animation = self.death_frames
        else:
            self.current_animation = (
                self.idle_left_frames if self.direction == "left"
                else self.idle_right_frames
            )

        self.animate(dt)

        # tornados
        for tornado in self.tornados[:]:
            tornado.update(dt)

            if tornado.dead:
                if tornado in self.tornados:
                    self.tornados.remove(tornado)
            elif tornado.collides_with_player(player):
                player.take_damage(1)
                self.tornados.remove(tornado)
            elif tornado.sprite.x < -200 or tornado.sprite.x > 1700:
                self.tornados.remove(tornado)

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self):
        self.sprite.draw()
        self.draw_hp_bar()
        for tornado in self.tornados:
            tornado.draw()
