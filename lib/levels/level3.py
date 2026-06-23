import pygame
from pplay.window import Window
from pplay.keyboard import Keyboard
from pplay.sprite import Sprite

from lib.boss.corpo_seco import *
from lib.boss.platform import *

# ─── Dimensões da tela ──────────────────────────────────────────────────────
WIN_W = 1920
WIN_H = 1080

FLOOR_Y = WIN_H - 250  # y do chão onde o player pisa = 1040

# ─── Layout das plataformas ──────────────────────────────────────────────────
TALL_TOP_Y = 260        # plataforma superior (≈ 33% da altura)
TALL_H = FLOOR_Y - TALL_TOP_Y
MID_TOP_Y = 520         # plataforma inferior (≈ 57% da altura)
MID_H = 300
PLAT_W = 590            # largura (~30% da tela)

TALL_POSITIONS = [630, 1400]  # 1 plataforma superior esquerda
MID_POSITIONS = [630, 1400]  # 1 plataforma inferior esquerda (mesma coluna)

# ─── Offsets visuais da plataformam3 (317×154) ──────────────────────────────
# Medidos a partir do sprite: margem transparente esquerda e no topo
# antes dos pixels opacos da superfície de pedra.
PLAT_OFFSET_X = 30    # colunas transparentes à esquerda
PLAT_OFFSET_Y = 18    # linhas transparentes no topo
PLAT_VISIBLE_W = 269   # largura real da superfície visível

DROP_DURATION = 0.4   # segundos


class Level3:
    """
    Fase 3 completa.

    Interface pública
    -----------------
    update(keyboard, dt) → None | "win" | "lose" | "menu"
    draw()
    """

    def __init__(self, window: Window, dt=60):
        self.window = window

        # ── Fundo ────────────────────────────────────────────────────────────
        try:
            self.bg = Sprite("sprites/wallpaper/level/lvl3.png")
        except Exception:
            self.bg = None

        self.fps = int(1/60)
        self.cooldown_fps = 2
        self.dt = 0 if dt == 0 else 60

        # ── Player ───────────────────────────────────────────────────────────
        from lib.player import Player
        self.player = Player(window)
        self.player.sprite.x = 200
        self.player.sprite.y = FLOOR_Y - self.player.sprite.height

        # Física vertical gerenciada por Level2
        self.player.external_physics = True
        self.player.FLOOR_Y = FLOOR_Y

        # Timer de drop-through
        self._drop_timer = 0.0

        # ── Boss ─────────────────────────────────────────────────────────────
        self.corpo_seco = CorpoSeco(window)

        # ── Plataformas ──────────────────────────────────────────────────────
        # Cada Platform recebe a posição do sprite + os offsets visuais,
        # para que o hitbox de colisão fique exatamente na superfície visível.
        self.platforms: list[Platform] = []

        for cx in TALL_POSITIONS:
            sx = cx - PLAT_W // 2          # x do sprite
            self.platforms.append(Platform(
                x=sx,
                y=TALL_TOP_Y,
                w=PLAT_W,
                sprite_path="sprites/objects/mula/plataformas/plataformam3.png",
                offset_x=PLAT_OFFSET_X,
                offset_y=PLAT_OFFSET_Y,
                visible_w=PLAT_VISIBLE_W,
            ))

        for cx in MID_POSITIONS:
            sx = cx - PLAT_W // 2
            self.platforms.append(Platform(
                x=sx,
                y=MID_TOP_Y,
                w=PLAT_W,
                sprite_path="sprites/objects/mula/plataformas/plataformam3.png",
                offset_x=PLAT_OFFSET_X,
                offset_y=PLAT_OFFSET_Y,
                visible_w=PLAT_VISIBLE_W,
            ))

        # ── Estado da fase ───────────────────────────────────────────────────
        self._result = None
        self._dead_timer = 0.0

    # =========================================================
    # UPDATE PRINCIPAL
    # =========================================================

    def update(self, keyboard: Keyboard, dt: float):

        if self._result is not None:
            return self._result

        self._last_dt = dt
        self._handle_drop_through(keyboard, dt)

        # Física e resolução de colisão ANTES do update do player,
        # para que is_on_ground já esteja correto quando a animação
        # for escolhida (evita animação de pulo repetindo ao pousar).
        self._apply_gravity(dt)
        self._resolve_platforms()
        self._clamp_player()

        self.player.update(keyboard, dt)

        self.corpo_seco.update(dt, self.player)

        self._check_win_lose(dt)

        if keyboard.key_pressed("ESC"):
            return "menu"
        return self._result

    # =========================================================
    # DROP-THROUGH (descer de plataforma)
    # =========================================================

    def _handle_drop_through(self, kb: Keyboard, dt: float):
        p = self.player

        if self._drop_timer > 0:
            self._drop_timer -= dt
            p._drop_through = True
        else:
            p._drop_through = False

        space = kb.key_pressed("SPACE")
        down = kb.key_pressed("DOWN") or kb.key_pressed("S")

        if space and down and p.is_on_ground and self._drop_timer <= 0:
            self._drop_timer = DROP_DURATION
            p._drop_through = True

    # =========================================================
    # FÍSICA VERTICAL
    # =========================================================

    def _apply_gravity(self, dt: float):
        p = self.player
        p._prev_y = p.sprite.y
        if not p.is_on_ground:
            p.vel_y += p.gravity * dt
            p.sprite.y += p.vel_y * dt

    def _resolve_platforms(self):
        p = self.player
        prev_y = getattr(p, '_prev_y', p.sprite.y)
        landed = False

        for plat in self.platforms:
            if plat.check_landing(p, prev_y):
                p.sprite.y = plat.y - p.sprite.height
                p.vel_y = 0.0
                p.is_on_ground = True
                landed = True
                break

        if not landed and p.sprite.y + p.sprite.height >= FLOOR_Y:
            p.sprite.y = FLOOR_Y - p.sprite.height
            p.vel_y = 0.0
            p.is_on_ground = True
            landed = True

        if not landed:
            p.is_on_ground = False

    def _clamp_player(self):
        p = self.player
        if p.sprite.x < 0:
            p.sprite.x = 0
        if p.sprite.x + p.sprite.width > WIN_W:
            p.sprite.x = WIN_W - p.sprite.width
        if p.sprite.y < 0:
            p.sprite.y = 0
            if p.vel_y < 0:
                p.vel_y = 0

    # =========================================================
    # WIN / LOSE
    # =========================================================

    def _check_win_lose(self, dt: float):
        if self.corpo_seco.dead:
            self._dead_timer += dt
            if self._dead_timer >= 2.5:
                self._result = "win"
            return

        if getattr(self.player, "dead", False):
            self._result = "lose"

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self):
        surf = pygame.display.get_surface()

        if self.bg is not None:
            self.bg.draw()
        else:
            surf.fill((20, 15, 30))

        for plat in self.platforms:
            plat.draw()

        pygame.draw.line(surf, (100, 70, 30),
                         (0, FLOOR_Y), (WIN_W, FLOOR_Y), 3)

        self.player.draw()
        self._draw_fps()
        self.corpo_seco.draw()
        self._draw_hud()

    def _draw_hud(self):
        self.window.draw_text(
            f"Corpo seco –",
            WIN_W // 2 - 80, 5,
            size=22, color=(255, 220, 80)
        )
        life = "❤️" * self.player.life + "💔" * (3 - self.player.life)
        self.window.draw_text(life, 10, 40, size=20, color=(255, 255, 255))

    def _draw_fps(self):
        if self.cooldown_fps < 0:
            self.dt = self.window.delta_time()
            self.cooldown_fps = 2
            self.fps = int(1 / self.dt) if self.dt > 0 else 0
        self.window.draw_text(f"FPS: {self.fps}",
                              10, 10, size=25, color=(255, 255, 255))
        self.cooldown_fps -= self.dt
