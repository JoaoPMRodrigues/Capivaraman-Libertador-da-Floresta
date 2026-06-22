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
        """
        prev_y: sprite.y do player no frame ANTERIOR ao movimento vertical.

        Pousa se:
          1. Player vinha de cima (prev_y + height <= self.y  antes do movimento)
          2. Agora esta abaixo do topo (sprite.y + height >= self.y)
          3. Horizontalmente dentro da plataforma
          4. Nao esta em modo drop-through
        """
        if player._drop_through:
            return False

        px = player.sprite.x
        pw = player.sprite.width
        ph = player.sprite.height

        # checa sobreposicao horizontal
        if px + pw <= self.x or px >= self.x + self.w:
            return False

        prev_feet = prev_y + ph
        curr_feet = player.sprite.y + ph

        # 1. Condição tradicional: passou pelo topo da plataforma neste frame
        if prev_feet <= self.y and curr_feet >= self.y:
            return True

        # 2. Correção do Bug: Se o player já estava no chão e a variação do sprite
        # mudou a posição dos pés levemente para cima ou para baixo (tolerância de 15 pixels)
        if player.is_on_ground and abs(curr_feet - self.y) <= 15:
            return True

        return False

    def draw(self):
        if self.sprite:
            self.sprite.draw()
