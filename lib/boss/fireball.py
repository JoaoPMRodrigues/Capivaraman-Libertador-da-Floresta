import pygame
from pplay.sprite import Sprite
from os import listdir
from lib.utils import resource_path


class Fireball:
    """
    Bola de fogo pequena (fase 1 e 2 da Mula).

    - Viaja da direita para a esquerda
    - Pode ser destruída com 3 tiros
    - Pode ser evitada pulando por cima
    """

    HP_MAX = 3
    DAMAGE = 1

    def __init__(self, x, player_y, window):

        self.window = window

        self.frames = self._load_frames(
            "sprites/boss/mula/fireball"
        )

        if self.frames:
            self.sprite = self.frames[0]
        else:
            raise FileNotFoundError(
                "Nenhum frame encontrado em "
                "'sprites/boss/mula/fireball'"
            )

        self.sprite.x = x
        self.sprite.y = player_y - self.sprite.height / 2

        self.speed = 500

        self.hp = self.HP_MAX
        self.dead = False

        self._frame_idx = 0
        self._anim_timer = 0
        self._anim_speed = 0.08

    # =====================================================
    # CARREGAMENTO
    # =====================================================

    def _load_frames(self, folder):

        real_folder = resource_path(folder)

        try:
            files = sorted(
                file
                for file in listdir(real_folder)
                if file.endswith(".png")
            )

            return [
                Sprite(f"{folder}/{file}")
                for file in files
            ]

        except FileNotFoundError:
            return []

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if self.dead:
            return

        self.sprite.x -= self.speed * dt

        if len(self.frames) <= 1:
            return

        self._anim_timer += dt

        if self._anim_timer >= self._anim_speed:

            self._anim_timer = 0

            self._frame_idx = (
                self._frame_idx + 1
            ) % len(self.frames)

            old_x = self.sprite.x
            old_y = self.sprite.y

            self.sprite = self.frames[self._frame_idx]

            self.sprite.x = old_x
            self.sprite.y = old_y

    # =====================================================
    # COMBATE
    # =====================================================

    def take_hit(self):

        self.hp -= 1

        if self.hp <= 0:
            self.dead = True
            return True

        return False

    def collides_with_player(self, player):

        if not self.sprite.collided(player.sprite):
            return False

        fireball_center_y = (
            self.sprite.y +
            self.sprite.height / 2
        )

        player_feet_y = (
            player.sprite.y +
            player.sprite.height
        )

        return player_feet_y >= fireball_center_y

    # =====================================================
    # UTIL
    # =====================================================

    def is_off_screen(self):

        return (
            self.sprite.x +
            self.sprite.width
        ) < 0

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        if self.dead:
            return

        self.sprite.draw()

        surf = pygame.display.get_surface()

        if not surf:
            return

        for i in range(self.HP_MAX):

            color = (
                (220, 80, 20)
                if i < self.hp
                else (50, 50, 50)
            )

            dx = int(
                self.sprite.x
                + self.sprite.width / 2
                - (self.HP_MAX * 10) / 2
                + i * 10
            )

            dy = int(self.sprite.y) - 12

            pygame.draw.rect(
                surf,
                color,
                (dx, dy, 8, 8)
            )


class SuperFireball:
    """
    Bola de fogo grande (fase 2 da Mula).

    - Ocupa um corredor inteiro
    - Não pode ser destruída
    - Causa dano elevado
    - Viaja da direita para a esquerda
    """

    DAMAGE = 3

    CORRIDOR_Y = {
        "chao": 200,
        "meio": 350,
        "topo": 900,
    }

    def __init__(self, x, corridor, window):

        self.window = window
        self.corridor = corridor

        self.frames = self._load_frames(
            "sprites/boss/mula/super-fireball"
        )

        if self.frames:
            self.sprite = self.frames[0]
        else:
            raise FileNotFoundError(
                "Nenhum frame encontrado em "
                "'sprites/boss/mula/super-fireball'"
            )

        center_y = self.CORRIDOR_Y.get(corridor, 590)

        self.sprite.x = x
        self.sprite.y = center_y - self.sprite.height / 2

        self.speed = 400
        self.dead = False

        self._frame_idx = 0
        self._anim_timer = 0
        self._anim_speed = 0.10

    # Carrega frames

    def _load_frames(self, folder):

        real_folder = resource_path(folder)

        try:
            files = sorted(
                file
                for file in listdir(real_folder)
                if file.endswith(".png")
            )

            return [
                Sprite(f"{folder}/{file}")
                for file in files
            ]

        except FileNotFoundError:
            return []

    # Update

    def update(self, dt):

        if self.dead:
            return

        self.sprite.x -= self.speed * dt

        if len(self.frames) <= 1:
            return

        self._anim_timer += dt

        if self._anim_timer >= self._anim_speed:

            self._anim_timer = 0

            self._frame_idx = (
                self._frame_idx + 1
            ) % len(self.frames)

            old_x = self.sprite.x
            old_y = self.sprite.y

            self.sprite = self.frames[self._frame_idx]

            self.sprite.x = old_x
            self.sprite.y = old_y

    # Colisão com player

    def collides_with_player(self, player):

        margin_x = 30
        margin_y = 30

        fb_left = self.sprite.x + margin_x
        fb_right = (
            self.sprite.x
            + self.sprite.width
            - margin_x
        )

        fb_top = self.sprite.y + margin_y
        fb_bottom = (
            self.sprite.y
            + self.sprite.height
            - margin_y
        )

        pl_left = player.sprite.x
        pl_right = (
            player.sprite.x
            + player.sprite.width
        )

        pl_top = player.sprite.y
        pl_bottom = (
            player.sprite.y
            + player.sprite.height
        )

        return (
            pl_right > fb_left
            and pl_left < fb_right
            and pl_bottom > fb_top
            and pl_top < fb_bottom
        )

    # Verifica fora da tela

    def is_off_screen(self):

        return (
            self.sprite.x +
            self.sprite.width
        ) < 0

    # Draw
    def draw(self):

        if not self.dead:
            self.sprite.draw()
