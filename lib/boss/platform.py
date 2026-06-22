from pplay.sprite import Sprite


class Platform:
    """
    Plataforma invisivel (logica pura) com sprite visual opcional.

    x, y       : canto superior esquerdo da superficie onde o player pousa
    w          : largura da superficie de colisao
    sprite_top : sprite da superficie (ex: madeira/pedra do topo)
    """

    def __init__(self, x: int, y: int, w: int, sprite_path: str = None):
        self.x = x
        self.y = y
        self.w = w
        self.sprite_path = sprite_path

        if sprite_path:
            self.sprite = Sprite(sprite_path)
            self.sprite.x = x
            self.sprite.y = y
        else:
            self.sprite = None

    # Colisao de cima para baixo (one-way platform)
    # Retorna True se o player POUSOU ou ESTÁ mantido nesta plataforma

    def check_landing(self, player, prev_y: float) -> bool:
        if player._drop_through:
            return False

        px = player.sprite.x
        pw = player.sprite.width
        ph = player.sprite.height

        # Sobreposição horizontal
        if px + pw <= self.x or px >= self.x + self.w:
            return False

        prev_feet = prev_y + ph
        curr_feet = player.sprite.y + ph

        # Atravessou o topo da plataforma neste frame
        if prev_feet <= self.y <= curr_feet:
            return True

        # Já estava sobre a plataforma no frame anterior
        if abs(prev_feet - self.y) <= 5 and player.vel_y >= 0:
            return True

        return False

    def draw(self):
        if self.sprite:
            self.sprite.draw()
