
import pygame

# ─── Dimensões e cores padrão ────────────────────────────────────────────────
COLOR_TALL = (100, 60,  20)
COLOR_MID = (140, 80,  30)
COLOR_TOP = (180, 120, 50)
TOP_H = 16   # espessura da superfície pisável


class Platform:
    """
    Plataforma one-way.

    Parâmetros
    ----------
    x, y   : canto superior-esquerdo.
    width  : largura da plataforma.
    height : altura total do bloco.
    kind   : "tall" | "mid"  (só afeta a cor).
    """

    def __init__(self, x: int, y: int, width: int, height: int, kind: str = "mid"):
        self.rect = pygame.Rect(x, y, width, height)
        self.kind = kind
        self.color = COLOR_TALL if kind == "tall" else COLOR_MID
        self.top_rect = pygame.Rect(x, y, width, TOP_H)

    # ── Lógica de colisão ────────────────────────────────────────────────────

    def resolve_player(self, player, _dt) -> bool:
        """
        Testa colisão one-way e corrige posição do player.
        Retorna True se o player pousou nesta plataforma.

        Ignora colisão quando:
          - player.vel_y < 0  (subindo — atravessa de baixo)
          - player._drop_through == True  (descendo intencionalmente)
        """
        # Sobe de baixo ou quer descer → sem colisão
        if player.vel_y < 0 or getattr(player, "_drop_through", False):
            return False

        px = player.sprite.x
        py = player.sprite.y
        pw = player.sprite.width
        ph = player.sprite.height

        prect = pygame.Rect(int(px), int(py), int(pw), int(ph))

        if not prect.colliderect(self.top_rect):
            return False

        # Base do player deve estar cruzando o topo da plataforma
        player_bottom = py + ph
        platform_top = self.rect.y
        platform_top_b = self.rect.y + TOP_H + 6   # tolerância

        if platform_top <= player_bottom <= platform_top_b and player.vel_y >= 0:
            player.sprite.y = platform_top - ph
            player.vel_y = 0.0
            player.is_on_ground = True
            return True

        return False

    # ── Renderização ─────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, COLOR_TOP,
                         pygame.Rect(self.rect.x, self.rect.y,
                                     self.rect.width, TOP_H))
