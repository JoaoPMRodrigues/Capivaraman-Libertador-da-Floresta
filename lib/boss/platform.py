from pplay.sprite import Sprite


class Platform:
    """
    Plataforma com sprite visual e hitbox alinhado à parte visível do sprite.

    Parâmetros
    ----------
    x, y        : posição do canto superior-esquerdo do SPRITE (não do hitbox)
    w           : largura total do sprite
    sprite_path : caminho para o sprite
    offset_x    : margem transparente esquerda do sprite até a superfície visível
    offset_y    : margem transparente no topo do sprite até a superfície visível
    visible_w   : largura real da superfície visível (hitbox de colisão)

    Se offset_x/offset_y/visible_w não forem informados, o hitbox cobre o
    sprite inteiro (comportamento legado).
    """

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        sprite_path: str = None,
        offset_x: int = 0,
        offset_y: int = 0,
        visible_w: int = None,
    ):
        self.sprite_x = x          # posição do sprite
        self.sprite_y = y

        # Hitbox: alinhado ao pixel visível do sprite
        self.x = x + offset_x                          # topo-esquerdo da colisão
        self.y = y + offset_y                          # topo da superfície de colisão
        self.w = visible_w if visible_w is not None else w
        self.offset_x = offset_x
        self.offset_y = offset_y

        if sprite_path:
            self.sprite = Sprite(sprite_path)
            self.sprite.x = x
            self.sprite.y = y
        else:
            self.sprite = None

    # ------------------------------------------------------------------
    # Colisão one-way (só de cima para baixo)
    # Retorna True se o player pousou ou está mantido nesta plataforma
    # ------------------------------------------------------------------

    def check_landing(self, player, prev_y: float) -> bool:
        if player._drop_through:
            return False

        px = player.sprite.x
        pw = player.sprite.width
        ph = player.sprite.height

        # Sobreposição horizontal com o hitbox visível
        if px + pw <= self.x or px >= self.x + self.w:
            return False

        prev_feet = prev_y + ph
        curr_feet = player.sprite.y + ph

        # Atravessou o topo da plataforma neste frame
        if prev_feet <= self.y <= curr_feet:
            return True

        # Já estava sobre a plataforma no frame anterior (tolerância de 5px)
        if abs(prev_feet - self.y) <= 5 and player.vel_y >= 0:
            return True

        return False

    def draw(self):
        if self.sprite:
            self.sprite.draw()
