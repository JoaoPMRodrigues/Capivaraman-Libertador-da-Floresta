
import pygame
from pplay.window import Window
from pplay.keyboard import Keyboard
from pplay.sprite import Sprite

from lib.boss.mula import Mula
from lib.boss.fireball import SuperFireball
from lib.platform import Platform
from lib.flamethrower import Flamethrower

# ─── Dimensões da tela ──────────────────────────────────────────────────────
WIN_W = 1920
WIN_H = 720

FLOOR_Y = WIN_H - 40   # y do chão onde o player pisa

# ─── Layout das plataformas ──────────────────────────────────────────────────
TALL_TOP_Y = 80
TALL_H = FLOOR_Y - TALL_TOP_Y
MID_TOP_Y = 380
MID_H = 200
PLAT_W = 80

TALL_POSITIONS = [320, 900]   # X do centro de cada coluna tall
MID_POSITIONS = [320, 900]   # X do centro de cada bloco mid

# ─── Corredores da SuperFireball ────────────────────────────────────────────
CORRIDOR_Y = {
    "topo": TALL_TOP_Y + 80,   # ≈ 160
    "meio": MID_TOP_Y - 50,   # ≈ 330
    "chao": FLOOR_Y - 70,   # ≈ 610
}

# ─── Posições X das lanças-chama ─────────────────────────────────────────────
FLAME_POSITIONS = [550, 750, 1200]

# ─── Tempo de passthrough ao descer de plataforma ────────────────────────────
DROP_DURATION = 0.4   # segundos


class Level2:
    """
    Fase 2 completa.

    Interface pública
    -----------------
    update(keyboard, dt) → None | "win" | "lose" | "menu"
    draw()
    """

    def __init__(self, window: Window):
        self.window = window

        # ── Injeta corredores antes de criar a Mula ──────────────────────────
        SuperFireball.CORRIDOR_Y = CORRIDOR_Y

        # ── Fundo ────────────────────────────────────────────────────────────
        try:
            self.bg = Sprite("sprites/wallpaper/level/lvl2.png")
        except Exception:
            self.bg = None

        # ── Player ───────────────────────────────────────────────────────────
        from lib.player import Player
        self.player = Player(window)
        self.player.sprite.x = 150
        self.player.sprite.y = FLOOR_Y - self.player.sprite.height

        # Ativa física externa: player.update() cuida de input, animação e
        # tiros, mas NÃO aplica gravidade nem limita pelo FLOOR_Y.
        self.player.external_physics = True
        self.player.FLOOR_Y = FLOOR_Y      # atualiza chão para esta fase

        # Timer de drop-through (controla _drop_through do player)
        self._drop_timer = 0.0

        # ── Boss ─────────────────────────────────────────────────────────────
        self.mula = Mula(window)

        # ── Plataformas ──────────────────────────────────────────────────────
        self.platforms: list[Platform] = []

        for cx in TALL_POSITIONS:
            self.platforms.append(Platform(
                x=cx - PLAT_W // 2,
                y=TALL_TOP_Y,
                width=PLAT_W,
                height=TALL_H,
                kind="tall"
            ))

        for cx in MID_POSITIONS:
            self.platforms.append(Platform(
                x=cx - PLAT_W // 2,
                y=MID_TOP_Y,
                width=PLAT_W,
                height=MID_H,
                kind="mid"
            ))

        # ── Lanças-chama ──────────────────────────────────────────────────────
        self.flamers: list[Flamethrower] = [
            Flamethrower(x, FLOOR_Y, MID_TOP_Y)
            for x in FLAME_POSITIONS
        ]

        # ── Estado da fase ───────────────────────────────────────────────────
        self._result = None
        self._dead_timer = 0.0

    # =========================================================
    # UPDATE PRINCIPAL
    # =========================================================

    def update(self, keyboard: Keyboard, dt: float):
        if self._result is not None:
            return self._result

        # 1) Player: input, animação, tiros — física vertical pelo Level2
        self._handle_drop_through(keyboard, dt)
        self.player.update(keyboard, dt)

        # 2) Física vertical (gravidade + colisão de plataformas)
        self._apply_gravity(dt)
        self._resolve_platforms()
        self._clamp_player()

        # 3) Lanças-chama
        self._update_flamers(dt)

        # 4) Boss
        self.mula.update(dt, self.player)

        # 5) Win / Lose
        self._check_win_lose(dt)
        return self._result

    # =========================================================
    # DROP-THROUGH (descer de plataforma)
    # =========================================================

    def _handle_drop_through(self, kb: Keyboard, dt: float):
        """
        Detecta SPACE + DOWN ou SPACE + S para descer da plataforma.
        Ativa player._drop_through = True por DROP_DURATION segundos.
        """
        p = self.player

        if self._drop_timer > 0:
            self._drop_timer -= dt
            p._drop_through = True
        else:
            p._drop_through = False

        # Verifica novo acionamento
        space = kb.key_pressed("SPACE")
        down = kb.key_pressed("DOWN") or kb.key_pressed("S")

        if space and down and p.is_on_ground and self._drop_timer <= 0:
            self._drop_timer = DROP_DURATION
            p._drop_through = True
            # Impede que o player.update() interprete SPACE como pulo
            # momentaneamente: zeramos is_on_ground DEPOIS do update.
            # (O player só pula se is_on_ground=True no instante da detecção)

    # =========================================================
    # FÍSICA VERTICAL
    # =========================================================

    def _apply_gravity(self, dt: float):
        p = self.player
        if not p.is_on_ground:
            p.vel_y += p.gravity * dt
            p.sprite.y += p.vel_y * dt

    def _resolve_platforms(self):
        p = self.player
        landed = False

        # ── Chão da fase ────────────────────────────────────────────────────
        if p.sprite.y + p.sprite.height >= FLOOR_Y:
            p.sprite.y = FLOOR_Y - p.sprite.height
            p.vel_y = 0.0
            landed = True

        # ── Plataformas one-way ───────────────────────────────────────────────
        if not p._drop_through:
            for plat in self.platforms:
                if plat.resolve_player(p, 0):
                    landed = True

        p.is_on_ground = landed

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
    # LANÇAS-CHAMA
    # =========================================================

    def _update_flamers(self, dt: float):
        for fl in self.flamers:
            fl.update(dt)
            if fl.collides_with_player(self.player):
                self.player.take_damage(1)

    # =========================================================
    # WIN / LOSE
    # =========================================================

    def _check_win_lose(self, dt: float):
        if self.mula.dead:
            self._dead_timer += dt
            if self._dead_timer >= 2.5:
                self._result = "win"
            return

        # player.dead é setado em player.take_damage quando life <= 0
        if getattr(self.player, "dead", False):
            self._result = "lose"

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self):
        surf = pygame.display.get_surface()

        # Fundo
        if self.bg is not None:
            self.bg.draw()
        else:
            surf.fill((20, 15, 30))

        # Plataformas
        for plat in self.platforms:
            plat.draw(surf)

        # Lanças-chama
        for fl in self.flamers:
            fl.draw(surf)

        # Linha do chão
        pygame.draw.line(surf, (100, 70, 30),
                         (0, FLOOR_Y), (WIN_W, FLOOR_Y), 3)

        # Linha de aviso de corredor (fase 2 da Mula)
        if self.mula.charging and self.mula._charge_corridor:
            cy = CORRIDOR_Y.get(self.mula._charge_corridor, 0)
            if cy:
                warn_surf = pygame.Surface((WIN_W, 3), pygame.SRCALPHA)
                warn_surf.fill((255, 60, 0, 160))
                surf.blit(warn_surf, (0, cy))

        # Player
        self.player.draw()

        # Boss
        self.mula.draw()

        # HUD
        self._draw_hud()

    def _draw_hud(self):
        phase_txt = "FASE 2" if self.mula._is_phase2() else "FASE 1"
        self.window.draw_text(
            f"Mula – {phase_txt}",
            WIN_W // 2 - 80, 5,
            size=22, color=(255, 220, 80)
        )
