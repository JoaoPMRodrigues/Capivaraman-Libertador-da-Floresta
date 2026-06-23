import pygame
from pplay.sprite import Sprite
from os import listdir


class Fireball:
    """
    Bola de fogo pequena (fase 1 e 2 da Mula).
    - Viaja da direita para a esquerda na altura do jogador
    - Destruida com 3 tiros
    - Pular por cima evita dano
    """
    HP_MAX = 3
    DAMAGE = 1

    def __init__(self, x, player_y, window):
        self.window = window
        self._load_frames("sprites/boss/mula/fireball")
        self.sprite.x = x
        self.sprite.y = player_y - self.sprite.height / 2

        self.speed = 500
        self.hp = self.HP_MAX
        self.dead = False

        self._frame_idx = 0
        self._anim_timer = 0.0
        self._anim_speed = 0.08

    def _load_frames(self, path):
        files = sorted(f for f in listdir(path) if f.endswith(".png"))
        self.frames = [Sprite(f"{path}/{f}") for f in files]
        self.sprite = self.frames[0]

    def update(self, dt):
        if self.dead:
            return
        self.sprite.x -= self.speed * dt
        self._anim_timer += dt
        if self._anim_timer >= self._anim_speed:
            self._anim_timer = 0
            self._frame_idx = (self._frame_idx + 1) % len(self.frames)
            old_x, old_y = self.sprite.x, self.sprite.y
            self.sprite = self.frames[self._frame_idx]
            self.sprite.x, self.sprite.y = old_x, old_y

    def take_hit(self) -> bool:
        """Retorna True se foi destruida."""
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def collides_with_player(self, player) -> bool:
        if not self.sprite.collided(player.sprite):
            return False
        # pulo por cima evita dano
        fb_center_y = self.sprite.y + self.sprite.height / 2
        player_feet_y = player.sprite.y + player.sprite.height
        return player_feet_y >= fb_center_y

    def is_off_screen(self):
        return self.sprite.x < -200

    def draw(self):
        if self.dead:
            return
        self.sprite.draw()
        # indicador de HP (pontinhos acima da fireball)
        surf = pygame.display.get_surface()
        if surf:
            for i in range(self.HP_MAX):
                color = (220, 80, 20) if i < self.hp else (50, 50, 50)
                dx = int(self.sprite.x + self.sprite.width / 2
                         - (self.HP_MAX * 10) / 2 + i * 10)
                dy = int(self.sprite.y) - 12
                pygame.draw.rect(surf, color, (dx, dy, 8, 8))


class SuperFireball:
    """
    Bola de fogo grande (fase 2 da Mula).
    - Ocupa um corredor inteiro: chao, meio ou topo
    - Causa 2 de dano
    - Nao pode ser destruida
    - Viaja da direita para a esquerda
    """
    DAMAGE = 3
    # Y do centro de cada corredor — ajuste conforme o layout do level2
    CORRIDOR_Y = {
        "chao": 200,   # corredor do chao
        "meio": 350,   # corredor das plataformas medias
        "topo": 900,   # corredor das plataformas grandes
    }

    def __init__(self, x, corridor: str, window):
        self.window = window
        self.corridor = corridor
        self._load_frames("sprites/boss/mula/super-fireball")

        center_y = self.CORRIDOR_Y.get(corridor, 590)
        self.sprite.x = x
        self.sprite.y = center_y - self.sprite.height / 2

        self.speed = 400
        self.dead = False

        self._frame_idx = 0
        self._anim_timer = 0.0
        self._anim_speed = 0.1

    def _load_frames(self, path):
        files = sorted(f for f in listdir(path) if f.endswith(".png"))
        self.frames = [Sprite(f"{path}/{f}") for f in files]
        self.sprite = self.frames[0]

    def update(self, dt):
        if self.dead:
            return
        self.sprite.x -= self.speed * dt
        self._anim_timer += dt
        if self._anim_timer >= self._anim_speed:
            self._anim_timer = 0
            self._frame_idx = (self._frame_idx + 1) % len(self.frames)
            old_x, old_y = self.sprite.x, self.sprite.y
            self.sprite = self.frames[self._frame_idx]
            self.sprite.x, self.sprite.y = old_x, old_y

    def collides_with_player(self, player) -> bool:
        margin_x = 30
        margin_y = 30

        fb_left = self.sprite.x + margin_x
        fb_right = self.sprite.x + self.sprite.width - margin_x

        fb_top = self.sprite.y + margin_y
        fb_bottom = self.sprite.y + self.sprite.height - margin_y

        pl_left = player.sprite.x
        pl_right = player.sprite.x + player.sprite.width

        pl_top = player.sprite.y
        pl_bottom = player.sprite.y + player.sprite.height

        return (
        pl_right > fb_left
        and pl_left < fb_right
        and pl_bottom > fb_top
        and pl_top < fb_bottom
        )

    def is_off_screen(self):
        return self.sprite.x < -300

    def draw(self):
        if not self.dead:
            self.sprite.draw()
