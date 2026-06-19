from lib.boss import *
from pplay.sprite import *
from random import randint
from os import listdir

from lib.tornado import *

# Y do chao compartilhado com o player
FLOOR_Y = 375


class Saci(Boss):

    def __init__(self, window):

        super().__init__(
            "sprites/boss/saci/idle_left/saci_idle1.png",
            window, 1350, FLOOR_Y, 100)

        self.window = window

        # Saci so tem dois lados: direita (inicio) e esquerda
        # O Y e sempre FLOOR_Y — mesma altura do jogador
        # X sera ajustado em _fix_positions() para considerar largura do sprite
        self._raw_positions = [
            (1350, FLOOR_Y),   # 0: direita
            (25,  FLOOR_Y),   # 1: esquerda
        ]
        self.positions        = list(self._raw_positions)
        self.current_position = 0   # comeca na direita

        # animacoes
        self.idle_right_frames = self._load_frames("sprites/boss/saci/idle_right")
        self.idle_left_frames  = self._load_frames("sprites/boss/saci/idle_left")
        self.attack_frames     = self._load_frames("sprites/boss/saci/attack")
        self.hit_frames        = self._load_frames("sprites/boss/saci/hit")
        self.death_frames      = self._load_frames("sprites/boss/saci/death")

        self.dead              = False
        self.frame             = 0
        self.animation_timer   = 0
        self.animation_speed   = 0.4
        self.current_animation = self.idle_left_frames

        # combate
        self.tornados         = []
        self.attack_timer     = 0
        self.attack_cooldown  = 3

        self.teleport_timer    = 0
        self.teleport_cooldown = 6

        # dash: movimento horizontal de um lado ao outro
        self.dashing    = False
        self.dash_speed = 1300
        self.direction  = "left"   # comeca olhando para o jogador

        self.hit_timer    = 0
        self.hit_duration = 0.2

        self._fix_positions()

    # =========================================================
    # HELPERS
    # =========================================================

    def _load_frames(self, path):
        files = sorted(f for f in listdir(path) if f.endswith(".png"))
        return [Sprite(f"{path}/{f}") for f in files]

    def _fix_positions(self):
        """Ajusta X para sprite nao sair da tela e Y para FLOOR_Y correto."""
        h  = self.sprite.height
        w  = self.sprite.width
        ww = self.window.width
        wh = self.window.height

        # Y: base do sprite no chao (FLOOR_Y e o topo do sprite)
        floor_y_clamped = max(0, min(FLOOR_Y, wh - h))

        self.positions = [
            (max(0, min(x, ww - w)), floor_y_clamped)
            for (x, _) in self._raw_positions
        ]

        # reposiciona para o inicio (direita)
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
            self.sprite   = self.current_animation[self.frame]
            self.sprite.x = old_x
            self.sprite.y = old_y

    # =========================================================
    # TELEPORTE
    # Alterna apenas entre esquerda e direita, mesmo Y do jogador
    # =========================================================

    def teleport(self):
        # vai sempre para o lado oposto ao atual
        new_pos = 1 if self.current_position == 0 else 0

        self.current_position = new_pos
        self.sprite.x = self.positions[new_pos][0]
        self.sprite.y = self.positions[new_pos][1]

        # olha para o centro da arena
        self.direction = "right" if new_pos == 1 else "left"

    # =========================================================
    # ATAQUE: TORNADO
    # =========================================================

    def throw_tornado(self, player):
        player_feet_y = player.sprite.y + player.sprite.height

        if self.direction == "left":
            launch_x = self.sprite.x
        else:
            launch_x = self.sprite.x + self.sprite.width

        tornado = Tornado(launch_x, player_feet_y, self.direction)
        self.tornados.append(tornado)

    # =========================================================
    # DASH
    # Saci da dash do lado em que esta para o lado oposto.
    # Fica no destino ate o proximo dash ser acionado.
    # O jogador pode pular por cima do Saci em dash para evitar dano.
    # =========================================================

    def try_dash(self):
        """Inicia o dash se nao estiver em dash e hp <= 50."""
        if not self.dashing:
            self.dashing = True
            self.state   = "dash"

            # define destino: lado oposto ao atual
            if self.current_position == 0:   # esta na direita → vai para esquerda
                self.dash_target = 1
                self.direction   = "left"
            else:                             # esta na esquerda → vai para direita
                self.dash_target = 0
                self.direction   = "right"

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
            self.sprite.x         = dest_x
            self.sprite.y         = dest_y
            self.current_position = self.dash_target
            self.dashing          = False
            self.state            = "idle"
            # vira para o centro apos parar
            self.direction = "right" if self.current_position == 1 else "left"

        # seguranca de limites
        self.sprite.x = max(0, min(self.sprite.x, ww - sw))

        # colisao com player durante dash:
        # pular por cima evita dano (mesma logica do tornado)
        if self._dash_hits_player(player):
            player.take_damage(1)

    def _dash_hits_player(self, player) -> bool:
        """Retorna True se o dash acerta o jogador (pulo por cima evita)."""
        if not self.sprite.collided(player.sprite):
            return False

        saci_center_y   = self.sprite.y + self.sprite.height / 2
        player_feet_y   = player.sprite.y + player.sprite.height

        # jogador pulou por cima: pes acima do centro do Saci
        if player_feet_y < saci_center_y:
            return False

        return True

    # =========================================================
    # DANO
    # =========================================================

    def check_bullets(self, player):
        for bullet in player.bullets[:]:

            # bala acertou o Saci
            if self.sprite.collided(bullet.sprite):
                self.take_damage(1)
                self.hit_timer = self.hit_duration
                player.bullets.remove(bullet)
                continue

            # bala acertou um tornado
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
            self.hp    = 0
            self.dead  = True
            self.state = "death"
            self.frame = 0
            self.current_animation = self.death_frames

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self, dt, player):

        if self.dead:
            self.tornados.clear()
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        self.attack_timer   += dt
        self.teleport_timer += dt

        # fase 2 (hp <= 50): dash aleatorio
        if self.hp <= 50 and not self.dashing:
            if randint(-200, 200) == 0:
                self.try_dash()

        # teleporte (so quando nao esta em dash)
        if not self.dashing and self.teleport_timer >= self.teleport_cooldown:
            self.teleport()
            self.teleport_timer = 0

        # ataque
        if self.attack_timer >= self.attack_cooldown:
            self.throw_tornado(player)
            self.attack_timer = 0

        self.update_dash(dt, player)
        self.check_bullets(player)

        # estado
        if self.hit_timer > 0:
            self.hit_timer -= dt
            self.state      = "hit"
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
