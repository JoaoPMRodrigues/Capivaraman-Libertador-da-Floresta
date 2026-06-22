

import pygame
import random

# ─── Constantes de tempo ────────────────────────────────────────────────────
WARN_TIME = 1.0   # segundos de aviso antes do ataque
ACTIVE_TIME = 1.2   # segundos com chamas ativas
COOLDOWN_MIN = 3.0  # cooldown mínimo entre ataques (por lança)
COOLDOWN_MAX = 7.0  # cooldown máximo

# ─── Cores ──────────────────────────────────────────────────────────────────
COLOR_BASE = (80,  40, 10)   # base da lança
COLOR_WARN = (255, 180,  0)  # brilho laranja de aviso
COLOR_FIRE1 = (255,  80,  0)  # chama externa
COLOR_FIRE2 = (255, 200,  0)  # chama interna
COLOR_WARN_GLOW = (255, 220, 80, 80)  # halo semitransparente

NOZZLE_W = 30   # largura do bico da lança
NOZZLE_H = 20

FLAME_W = 36   # largura da chama
# FLAME_H é dinâmico: do chão até as plataformas do meio


class Flamethrower:
    """
    Lança-chama individual.

    Parâmetros
    ----------
    x           : posição horizontal do centro da lança.
    floor_y     : y do chão da fase.
    mid_plat_y  : y do topo das plataformas do meio (limite superior da chama).
    """

    def __init__(self, x: int, floor_y: int, mid_plat_y: int):
        self.x = x
        self.floor_y = floor_y
        self.mid_plat_y = mid_plat_y

        # altura da chama
        self.flame_h = floor_y - mid_plat_y

        # rect do bico (para desenho)
        self.nozzle_rect = pygame.Rect(
            x - NOZZLE_W // 2,
            floor_y - NOZZLE_H,
            NOZZLE_W,
            NOZZLE_H
        )

        # rect de hitbox das chamas (colisão com player)
        self.flame_rect = pygame.Rect(
            x - FLAME_W // 2,
            mid_plat_y,
            FLAME_W,
            self.flame_h
        )

        # máquina de estados
        self.state = "idle"
        self.timer = random.uniform(0, COOLDOWN_MAX)  # offset inicial
        self.cooldown = random.uniform(COOLDOWN_MIN, COOLDOWN_MAX)

        # animação simples: oscilação das chamas
        self._anim_t = 0.0
        self._anim_spd = 8.0  # frequência da oscilação

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self._anim_t += dt * self._anim_spd

        if self.state == "idle":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "warning"
                self.timer = WARN_TIME

        elif self.state == "warning":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "active"
                self.timer = ACTIVE_TIME

        elif self.state == "active":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "idle"
                self.timer = self.cooldown
                self.cooldown = random.uniform(COOLDOWN_MIN, COOLDOWN_MAX)

    # ── Colisão ──────────────────────────────────────────────────────────────

    def is_active(self) -> bool:
        return self.state == "active"

    def collides_with_player(self, player) -> bool:
        if not self.is_active():
            return False

        px = int(player.sprite.x)
        py = int(player.sprite.y)
        pw = int(player.sprite.width)
        ph = int(player.sprite.height)

        prect = pygame.Rect(px, py, pw, ph)
        return prect.colliderect(self.flame_rect)

    # ── Desenho ──────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        # bico
        pygame.draw.rect(surface, COLOR_BASE, self.nozzle_rect)

        if self.state == "warning":
            self._draw_warning(surface)

        elif self.state == "active":
            self._draw_flame(surface)

    def _draw_warning(self, surface: pygame.Surface):
        """Faísca pulsante de aviso."""
        pulse = abs(pygame.math.Vector2(0, 1).rotate(self._anim_t * 60).y)
        r = int(255 * pulse)
        g = int(180 * pulse)
        color = (r, g, 0)

        spark_rect = pygame.Rect(
            self.x - 6,
            self.floor_y - NOZZLE_H - 12,
            12, 12
        )
        pygame.draw.ellipse(surface, color, spark_rect)

    def _draw_flame(self, surface: pygame.Surface):
        """Chamas animadas (várias elipses oscilantes)."""
        import math

        # chama externa
        for i in range(5):
            frac = i / 5.0
            ofs = int(math.sin(self._anim_t + i * 1.2) * 4)
            h_seg = int(self.flame_h * (1 - frac * 0.3))
            rect = pygame.Rect(
                self.x - FLAME_W // 2 + ofs,
                self.mid_plat_y + int(self.flame_h * frac * 0.05),
                FLAME_W - int(frac * 8),
                h_seg
            )
            alpha = max(0, 200 - int(frac * 100))
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill((*COLOR_FIRE1, alpha))
            surface.blit(s, (rect.x, rect.y))

        # chama interna (mais brilhante)
        inner_rect = pygame.Rect(
            self.x - FLAME_W // 4,
            self.mid_plat_y + self.flame_h // 3,
            FLAME_W // 2,
            self.flame_h * 2 // 3
        )
        pygame.draw.ellipse(surface, COLOR_FIRE2, inner_rect)
