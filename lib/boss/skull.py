import pygame
from os import listdir
from pplay.sprite import Sprite


class Skull:
    """
    Caveira lançada pelo Corpo Seco.
    Sempre se move para a esquerda.
    """
    HP_MAX = 5

    def __init__(self, x, player_y):
        # Tenta carregar os frames de animação da caveira
        path = "sprites/boss/corpo-seco/skull"
        self.frames = self._load_frames(path)

        if self.frames:
            self.sprite = Sprite(
                f"{path}/" + sorted(f for f in listdir(path) if f.endswith(".png"))[0])
        else:

            self.sprite = Sprite("sprites/boss/corpo-seco/idle/idle1.png")
            self.frames = [self.sprite]

        self.sprite.x = x
        self.sprite.y = player_y - (self.sprite.height / 2)

        self.speed = 650
        self.hp = self.HP_MAX
        self.dead = False

        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08

    def _load_frames(self, path):
        try:
            files = sorted(f for f in listdir(path) if f.endswith(".png"))
            return [Sprite(f"{path}/{f}") for f in files]
        except FileNotFoundError:
            return []

    def update(self, dt):
        if self.dead:
            return

        # Movimento estrito para a esquerda
        self.sprite.x -= self.speed * dt

        # Atualização dos frames
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.frames)

            old_x, old_y = self.sprite.x, self.sprite.y
            self.sprite = self.frames[self.frame]
            self.sprite.x = old_x
            self.sprite.y = old_y

    def take_hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def collides_with_player(self, player) -> bool:
        if not self.sprite.collided(player.sprite):
            return False

        # Ignora colisão se o jogador pular com os pés acima do centro da caveira
        tornado_center_y = self.sprite.y + self.sprite.height / 2
        player_feet_y = player.sprite.y + player.sprite.height

        if player_feet_y < tornado_center_y:
            return False

        return True

    def draw(self):
        if not self.dead:
            self.sprite.draw()

            # Barrinha de vida em blocos acima da caveira
            for i in range(self.HP_MAX):
                color = (220, 60, 60) if i < self.hp else (60, 60, 60)
                dot_x = int(self.sprite.x + self.sprite.width /
                            2 - (self.HP_MAX * 10) / 2 + i * 10)
                dot_y = int(self.sprite.y) - 14
                surf = pygame.display.get_surface()
                if surf:
                    pygame.draw.rect(surf, color, (dot_x, dot_y, 8, 8))
