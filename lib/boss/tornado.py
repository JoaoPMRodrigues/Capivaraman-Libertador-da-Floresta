from pplay.sprite import Sprite
from os import listdir

from lib.utils import resource_path


class Tornado:
    """
    Tornado lançado pelo Saci.

    - Surge na altura do jogador
    - Move-se horizontalmente
    - Possui animação
    - Pode ser destruído com tiros
    - Pode ser evitado pulando por cima
    """

    HP_MAX = 5

    def __init__(self, x, player_y, direction):

        self.frames = self._load_frames(
            "sprites/boss/saci/tornado"
        )

        if self.frames:
            self.sprite = self.frames[0]
        else:
            self.sprite = Sprite(
                resource_path(
                    "sprites/boss/saci/tornado/tornado1.png"
                )
            )
            self.frames = [self.sprite]

        self.sprite.x = x
        self.sprite.y = player_y - self.sprite.height

        self.direction = direction
        self.speed = 650

        self.hp = self.HP_MAX
        self.dead = False

        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08

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
            print(f"Pasta não encontrada: {folder}")
            return []

    # =====================================================
    # DANO
    # =====================================================

    def take_hit(self):

        self.hp -= 1

        if self.hp <= 0:
            self.dead = True
            return True

        return False

    # =====================================================
    # COLISÃO
    # =====================================================

    def collides_with_player(self, player):

        if not self.sprite.collided(player.sprite):
            return False

        tornado_center_y = (
            self.sprite.y +
            self.sprite.height / 2
        )

        player_feet_y = (
            player.sprite.y +
            player.sprite.height
        )

        return player_feet_y >= tornado_center_y

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if self.dead:
            return

        if self.direction == "left":
            self.sprite.x -= self.speed * dt
        else:
            self.sprite.x += self.speed * dt

        self.animation_timer += dt

        if (
            len(self.frames) > 1 and
            self.animation_timer >= self.animation_speed
        ):

            self.animation_timer = 0

            self.frame = (
                self.frame + 1
            ) % len(self.frames)

            old_x = self.sprite.x
            old_y = self.sprite.y

            self.sprite = self.frames[self.frame]

            self.sprite.x = old_x
            self.sprite.y = old_y

    # =====================================================
    # DESENHO
    # =====================================================

    def draw(self):

        if self.dead:
            return

        self.sprite.draw()
