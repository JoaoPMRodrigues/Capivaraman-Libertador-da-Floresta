from pplay.sprite import *
from os import listdir


class Tornado:
    """
    Tornado lancado pelo Saci.

    Mecanicas:
    - Nasce sempre na altura do jogador (nao do Saci)
    - Pode ser destruido com 4 tiros
    - Pode ser evitado pulando por cima (colisao desativa quando jogador
      esta acima do centro do tornado)
    - Anima com os frames disponíveis em sprites/boss/saci/tornado/
    """

    HP_MAX = 5   # tiros necessarios para destruir

    def __init__(self, x, player_y, direction):

        # carrega frames de animacao
        frames = self._load_frames("sprites/boss/saci/tornado")
        if frames:
            self.frames = frames
            self.sprite = Sprite("sprites/boss/saci/tornado/" + 
                sorted(f for f in listdir("sprites/boss/saci/tornado")
                       if f.endswith(".png"))[0])
        else:
            self.sprite = Sprite("sprites/boss/saci/tornado/tornado1.png")
            self.frames = [self.sprite]

        # posicao: X do Saci, Y alinhado ao jogador
        self.sprite.x = x
        self.sprite.y = player_y - self.sprite.height

        self.direction = direction
        self.speed     = 650

        self.hp        = self.HP_MAX
        self.dead      = False

        # animacao
        self.frame           = 0
        self.animation_timer = 0
        self.animation_speed = 0.08   # mais rapido que o boss para dar vida

    # =========================================================
    # HELPERS
    # =========================================================

    def _load_frames(self, path):
        try:
            files = sorted(f for f in listdir(path) if f.endswith(".png"))
            return [Sprite(f"{path}/{f}") for f in files]
        except FileNotFoundError:
            return []

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self, dt):
        if self.dead:
            return

        # movimento horizontal
        if self.direction == "left":
            self.sprite.x -= self.speed * dt
        else:
            self.sprite.x += self.speed * dt

        # animacao
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.frames)

            old_x = self.sprite.x
            old_y = self.sprite.y
            self.sprite   = self.frames[self.frame]
            self.sprite.x = old_x
            self.sprite.y = old_y

    def take_hit(self):
        """Chamado quando uma bala acerta o tornado. Retorna True se destruiu."""
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def collides_with_player(self, player) -> bool:
        """
        Retorna True so se o jogador estiver NA ALTURA do tornado.
        Se o jogador estiver acima do centro do tornado (pulando por cima),
        a colisao e ignorada — permitindo esquivar pulando.
        """
        if not self.sprite.collided(player.sprite):
            return False

        # Centro vertical do tornado
        tornado_center_y = self.sprite.y + self.sprite.height / 2

        # Base dos pes do jogador
        player_feet_y = player.sprite.y + player.sprite.height

        # Se os pes do jogador estao acima do centro do tornado, ele pulou por cima
        if player_feet_y < tornado_center_y:
            return False

        return True

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self):
        if not self.dead:
            self.sprite.draw()

            # barra de vida minima: pontos vermelhos acima do tornado
            for i in range(self.HP_MAX):
                color = (220, 60, 60) if i < self.hp else (60, 60, 60)
                # cada ponto tem 8x8 px, centrados sobre o tornado
                dot_x = int(self.sprite.x
                            + self.sprite.width / 2
                            - (self.HP_MAX * 10) / 2
                            + i * 10)
                dot_y = int(self.sprite.y) - 14
                # PPlay nao tem draw_rect — usa texto de bloco pequeno
                # (caracter de bloco solido em tamanho 10)
                from pplay.window import Window
                # acessa a janela globalmente via pygame para nao mudar API
                import pygame
                surf = pygame.display.get_surface()
                if surf:
                    pygame.draw.rect(surf, color, (dot_x, dot_y, 8, 8))
