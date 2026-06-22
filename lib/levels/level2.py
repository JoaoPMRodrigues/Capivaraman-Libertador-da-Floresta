
import pygame
from pplay.window import Window
from pplay.keyboard import Keyboard
from pplay.sprite import Sprite

from lib.boss.mula import Mula
from lib.boss.fireball import SuperFireball
from lib.boss.platform import Platform

# ─── Dimensões da tela ──────────────────────────────────────────────────────
WIN_W = 1920
WIN_H = 1080

FLOOR_Y = WIN_H - 40   # y do chão onde o player pisa = 1040

# ─── Layout das plataformas ──────────────────────────────────────────────────
TALL_TOP_Y = 360        # plataforma superior (≈ 33% da altura)
TALL_H = FLOOR_Y - TALL_TOP_Y
MID_TOP_Y = 620        # plataforma inferior (≈ 57% da altura)
MID_H = 300
PLAT_W = 590        # largura (~30% da tela)

TALL_POSITIONS = [630]  # 1 plataforma superior esquerda
MID_POSITIONS = [630]  # 1 plataforma inferior esquerda (mesma coluna)

# ─── Corredores da SuperFireball ────────────────────────────────────────────
CORRIDOR_Y = {
    # ≈ 300 (acima da plataforma alta)
    "topo": TALL_TOP_Y - 60,
    # ≈ 490 (entre as duas plataformas)
    "meio": (TALL_TOP_Y + MID_TOP_Y) // 2,
    "chao": FLOOR_Y - 90,                    # ≈ 950 (rente ao chão)
}

# ─── Posições X das lanças-chama ─────────────────────────────────────────────
FLAME_POSITIONS = [960, 1300, 1600]

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

    def __init__(self, window: Window, dt=60):
        self.window = window

        # ── Injeta corredores antes de criar a Mula ──────────────────────────
        SuperFireball.CORRIDOR_Y = CORRIDOR_Y

        # ── Fundo ────────────────────────────────────────────────────────────
        try:
            self.bg = Sprite("sprites/wallpaper/level/lvl2.png")
        except Exception:
            self.bg = None

        self.fps = int(1/60)
        self.cooldown_fps = 2
        self.dt = 0 if dt == 0 else 60
        # ── Player ───────────────────────────────────────────────────────────
        from lib.player import Player
        self.player = Player(window)
        self.player.sprite.x = 150
        self.player.sprite.y = FLOOR_Y - self.player.sprite.height  # usa o chão desta fase

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
                w=PLAT_W,
                sprite_path="sprites/objects/mula/plataformas/plataformam3.png",
            ))

        for cx in MID_POSITIONS:
            self.platforms.append(Platform(
                x=cx - PLAT_W // 2,
                y=MID_TOP_Y,
                w=PLAT_W,
                sprite_path="sprites/objects/mula/plataformas/plataformam3.png",
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

        # 1) Player: input, animação, tiros — física vertical pelo Level2
        self._handle_drop_through(keyboard, dt)
        self.player.update(keyboard, dt)

        # 2) Física vertical (gravidade + colisão de plataformas)
        self._apply_gravity(dt)
        self._resolve_platforms()
        self._clamp_player()

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
        p._prev_y = p.sprite.y          # posição antes de mover — usada por check_landing
        if not p.is_on_ground:
            p.vel_y += p.gravity * dt
            p.sprite.y += p.vel_y * dt

    def _resolve_platforms(self):
        p = self.player
        prev_y = getattr(p, '_prev_y', p.sprite.y)
        landed = False

        # ── Plataformas one-way ──────────────────────────────────────────────
        for plat in self.platforms:
            if plat.check_landing(p, prev_y):
                p.sprite.y = plat.y - p.sprite.height
                p.vel_y = 0.0
                landed = True
                break   # uma plataforma por frame é suficiente

        # ── Chão da fase ────────────────────────────────────────────────────
        if p.sprite.y + p.sprite.height >= FLOOR_Y:
            p.sprite.y = FLOOR_Y - p.sprite.height
            p.vel_y = 0.0
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
            plat.draw()

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

        # Fps
        self._draw_fps()
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
        # Vida do jogador
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

    def _handle_drop_through(self, kb: Keyboard, dt: float):
        """
        Detecta SPACE + DOWN ou SPACE + S para descer da plataforma.
        Ativa player._drop_through = True por DROP_DURATION segundos.
        """
        p = self.player

        # Garante o uso do delta time correto do sistema caso venha zerado/errado
        actual_dt = self.window.delta_time() if dt > 1 else dt

        if self._drop_timer > 0:
            self._drop_timer -= actual_dt
            p._drop_through = True
        else:
            p._drop_through = False

        # Verifica novo acionamento
        space = kb.key_pressed("SPACE")
        down = kb.key_pressed("DOWN") or kb.key_pressed("S")

        if space and down and p.is_on_ground and self._drop_timer <= 0:
            self._drop_timer = DROP_DURATION
            p._drop_through = True
            p.is_on_ground = False

            # CORREÇÃO CRÍTICA: Zera a força de pulo para impedir o conflito
            # com o comando SPACE dentro de player.update()
            p.vel_y = 0.0
            p.jump_pressed_last = True
