

import pygame
import math

# ─── Velocidades ────────────────────────────────────────────────────────────
FIREBALL_SPEED = 420   # px / s
SUPERFIREBALL_SPEED = 340

# ─── Corredores da SuperFireball ────────────────────────────────────────────
# Valores ajustados depois que o Level2 inicializa; o boss importa este dict.
CORRIDOR_Y_DEFAULT = {
    "chao": 650,
    "meio": 430,
    "topo": 160,
}


class Fireball:
    """
    Bola de fogo pequena disparada na direção do jogador.

    Parâmetros
    ----------
    x        : posição X inicial (boca da Mula).
    player_y : Y do centro do jogador no momento do disparo.
    window   : window do PPlay (para dimensões).
    """

    RADIUS = 14
    HP = 3          # tiros necessários para destruir
    DAMAGE = 1          # dano ao player se colidir

    def __init__(self, x: int, player_y: int, window):
        self.window = window
        self.x = float(x)
        self.y = float(player_y)
        self.dead = False
        self.hp = self.HP

        # direção: sempre para a esquerda (Mula está na direita)
        self.vx = -FIREBALL_SPEED

        # animação de rotação
        self._angle = 0.0
        self._surf = self._make_surface()

        # rect de colisão
        self._update_rect()

    # ── Superfície visual ────────────────────────────────────────────────────

    def _make_surface(self) -> pygame.Surface:
        d = self.RADIUS * 2
        surf = pygame.Surface((d, d), pygame.SRCALPHA)
        # bola externa laranja
        pygame.draw.circle(surf, (255, 100, 0),
                           (self.RADIUS, self.RADIUS), self.RADIUS)
        # núcleo amarelo
        pygame.draw.circle(surf, (255, 240, 0),
                           (self.RADIUS, self.RADIUS), self.RADIUS // 2)
        return surf

    def _update_rect(self):
        r = self.RADIUS
        self.rect = pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self.x += self.vx * dt
        self._angle = (self._angle + 180 * dt) % 360
        self._update_rect()

    # ── Colisão ──────────────────────────────────────────────────────────────

    def take_hit(self) -> bool:
        """Recebe 1 tiro. Retorna True se foi destruída."""
        if self.dead:
            return True
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
        return self.dead

    def collides_with_player(self, player) -> bool:
        if self.dead:
            return False
        prect = pygame.Rect(
            int(player.sprite.x), int(player.sprite.y),
            int(player.sprite.width), int(player.sprite.height)
        )
        return self.rect.colliderect(prect)

    def is_off_screen(self) -> bool:
        return self.x < -self.RADIUS * 2

    # ── Desenho ──────────────────────────────────────────────────────────────

    def draw(self):
        surf = self.window._window   # pygame surface interna do PPlay
        rotated = pygame.transform.rotate(self._surf, self._angle)
        r = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, r.topleft)

        # indicador de HP restante (pequenos traços)
        for i in range(self.hp):
            px = int(self.x) - self.RADIUS + i * 10
            py = int(self.y) - self.RADIUS - 8
            pygame.draw.rect(surf, (255, 255, 0), (px, py, 7, 4))


class SuperFireball:
    """
    Bola de fogo grande que percorre um corredor horizontal inteiro.

    Parâmetros
    ----------
    x        : posição X inicial (boca da Mula).
    corridor : "chao" | "meio" | "topo"
    window   : window do PPlay.
    """

    RADIUS = 32
    DAMAGE = 2   # corações de dano

    # dicionário de Y por corredor — preenchido pelo Level2 na inicialização
    CORRIDOR_Y: dict = CORRIDOR_Y_DEFAULT.copy()

    def __init__(self, x: int, corridor: str, window):
        self.window = window
        self.corridor = corridor
        self.x = float(x)
        self.y = float(self.CORRIDOR_Y.get(corridor, 500))
        self.dead = False

        self.vx = -SUPERFIREBALL_SPEED

        self._angle = 0.0
        self._surf = self._make_surface()
        self._update_rect()

    def _make_surface(self) -> pygame.Surface:
        d = self.RADIUS * 2
        surf = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 40,  0),
                           (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(surf, (255, 120, 0),  (self.RADIUS,
                           self.RADIUS), self.RADIUS * 2 // 3)
        pygame.draw.circle(surf, (255, 240, 50),
                           (self.RADIUS, self.RADIUS), self.RADIUS // 3)
        return surf

    def _update_rect(self):
        r = self.RADIUS
        self.rect = pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def update(self, dt: float):
        self.x += self.vx * dt
        self._angle = (self._angle + 120 * dt) % 360
        self._update_rect()

    def collides_with_player(self, player) -> bool:
        if self.dead:
            return False
        prect = pygame.Rect(
            int(player.sprite.x), int(player.sprite.y),
            int(player.sprite.width), int(player.sprite.height)
        )
        return self.rect.colliderect(prect)

    def is_off_screen(self) -> bool:
        return self.x < -self.RADIUS * 2

    def draw(self):
        surf = self.window._window
        rotated = pygame.transform.rotate(self._surf, self._angle)
        r = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, r.topleft)

        # aura pulsante
        import math
        pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 12)
        aura_surf = pygame.Surface(
            ((self.RADIUS + pulse) * 2, (self.RADIUS + pulse) * 2),
            pygame.SRCALPHA
        )
        pygame.draw.circle(
            aura_surf,
            (255, 60, 0, 60),
            (self.RADIUS + pulse, self.RADIUS + pulse),
            self.RADIUS + pulse
        )
        surf.blit(aura_surf, (int(self.x) - self.RADIUS - pulse,
                              int(self.y) - self.RADIUS - pulse))
