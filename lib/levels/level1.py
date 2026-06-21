from pplay.window import Window
from pplay.sprite import Sprite
from pplay.keyboard import Keyboard

from lib.boss.saci import Saci
from lib.player import Player


class Level1:

    def __init__(self, window: Window):
        self.window = window
        self.name = "Floresta Primordial"
        self.level_number = 1

        self.bg = Sprite("sprites/wallpaper/level/lvl1.png")
        self.player = Player(window)
        self.saci = Saci(window)

        self._keyboard = Keyboard()
        self.dt = self.window.delta_time()
        self.cooldown_fps = 2
        self.fps = int(1/self.dt if self.dt > 0 else 0)
        # Controla o tempo antes do resultado
        self._result_pending: str | None = None
        self._result_timer = 1.5

    def update(self, keyboard: Keyboard, dt: float):
        self._keyboard = keyboard
        self.dt = dt

        self.player.update(keyboard, dt)
        self.saci.update(dt, self.player)

        # ── Resultado pendente: espera animação ──────────────────────
        if self._result_pending is not None:
            self._result_timer -= dt
            if self._result_timer <= 0:
                return self._result_pending
            return None

        # ── Derrota ──────────────────────────────────────────────────
        if self.player.dead:
            self._result_pending = "lose"
            self._result_timer = 1.5
            return None

        # ── Vitória ──────────────────────────────────────────────────
        if self.saci.dead:
            self._result_pending = "win"
            self._result_timer = 1.5
            return None

        # ── Atalho debug ─────────────────────────────────────────────
        if keyboard.key_pressed("ESC"):
            return "menu"

        return None

    def draw(self):
        self.bg.draw()

        # HUD: vida do jogador
        life = "❤️" * self.player.life + "💔" * (3 - self.player.life)
        self.window.draw_text(life, 10, 40, size=20, color=(255, 255, 255))

        self.player.draw()
        self.saci.draw()

        # FPS
        self._draw_fps()

    def _draw_fps(self):
        if self.cooldown_fps < 0:
            self.dt = self.window.delta_time()
            self.cooldown_fps = 2
            self.fps = int(1 / self.dt) if self.dt > 0 else 0
        self.window.draw_text(f"FPS: {self.fps}",
                              10, 10, size=25, color=(255, 255, 255))
        self.cooldown_fps -= self.dt
