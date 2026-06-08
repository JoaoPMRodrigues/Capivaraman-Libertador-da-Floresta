from pplay.sprite import Sprite
from pplay.keyboard import Keyboard
from lib.player import Player


# Fundo padrão de cada fase.  alterar os caminhos quando os assets de cada fase entiverem prontos
LEVEL_BACKGROUNDS = {
    1: "sprites/wallpaper/level/lvl1.png",
    2: "sprites/wallpaper/level/lvl1.png",   
    3: "sprites/wallpaper/level/lvl1.png",
    4: "sprites/wallpaper/level/lvl1.png",
    5: "sprites/wallpaper/level/lvl1.png",
}

LEVEL_NAMES = {
    1: "Floresta Primordial",
    2: "Pântano das Sombras",
    3: "Cavernas do Fogo",
    4: "Templo Maldito",
    5: "Domínio do Caos",
}


class LevelPlaceholder:
    def __init__(self, window, level_number: int):
        self.window = window
        self.level_number = level_number
        self.name = LEVEL_NAMES.get(level_number, f"Fase {level_number}")

        # ── Fundo ──────────────────────────────────────────────────────
        bg_path = LEVEL_BACKGROUNDS.get(level_number, LEVEL_BACKGROUNDS[2])
        self.bg = Sprite(bg_path)

        # ── Personagem ─────────────────────────────────────────────────
        self.player = Player(window)

        # ── Mensagem de debug ──────────────────────────────────────────
        self._msg_timer = 0.0
        self._msg_duration = 180.0   # segundos até auto-vencer (debug)
        self._countdown = self._msg_duration

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def update(self, keyboard: Keyboard, dt: float):
        # Atualiza o jogador
        self.player.update(keyboard, dt)

        # ── Condição de derrota ──────────────────────────────────────
        if self.player.dead:
            # aguarda animação terminar
            if self.player.death_timer <= 0:
                return "lose"
            return None

        # ── Debug: ESC = vence a fase ────────────────────────────────
        if keyboard.key_pressed("ESC"):
            return "win"

        # ── Auto-vencer após timer (opcional) ───────────────────────
        self._countdown -= dt
        if self._countdown <= 0:
            return "win"

        return None

    def draw(self):
        self.bg.draw()
        self.player.draw()

        # HUD de debug
        self._draw_hud()

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------

    def _draw_hud(self):
        w = self.window

        # Nome da fase
        w.draw_text(
            f"[ FASE {self.level_number} — {self.name} ]",
            w.width // 2 - 200, 10,
            size=26, color=(255, 230, 80)
        )

        # Instrução de debug
        w.draw_text(
            "[ DEBUG ] Pressione ESC para avançar de fase",
            w.width // 2 - 230, 50,
            size=18, color=(200, 200, 200)
        )

        # Contador regressivo
        secs = max(0, int(self._countdown))
        w.draw_text(
            f"Auto-avança em: {secs}s",
            w.width // 2 - 80, 80,
            size=16, color=(180, 180, 180)
        )

        # Vida do jogador
        life_str = "❤️" * self.player.life + "💔" * (3 - self.player.life)
        w.draw_text(life_str, 10, 40, size=20, color=(255, 255, 255))
