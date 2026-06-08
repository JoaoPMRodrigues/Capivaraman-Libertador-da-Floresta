from pplay.sprite import Sprite
from pplay.keyboard import Keyboard
from pplay.window import Window

from lib.button import Button
from lib.player import Player
from lib.saci import Saci
from lib.level_manager import LevelManager
from lib.level_select import LevelSelect
from lib.level_placeholder import LevelPlaceholder
from lib.transition import Transition


# ─────────────────────────────────────────────────────────────────────────────
# Fase 1
# ─────────────────────────────────────────────────────────────────────────────

class _Level1:

    def __init__(self, window: Window):
        self.window = window
        self.name = "Floresta Primordial"
        self.level_number = 1

        self.bg = Sprite("sprites/wallpaper/level/lvl1.png")
        self.player = Player(window)
        self.saci = Saci(window)

        self._keyboard = Keyboard()
        self.dt = 0.0

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
        dt = self.window.delta_time()
        fps = int(1 / dt) if dt > 0 else 0
        self.window.draw_text(f"FPS: {fps}", 10, 10, size=25, color=(255, 255, 255))


# ─────────────────────────────────────────────────────────────────────────────
# Game -
# ─────────────────────────────────────────────────────────────────────────────

class Game:

    def __init__(self, window: Window):
        self.window = window
        self.keyboard = Keyboard()
        self.dt = 0.0

        # ── Estado ───────────────────────────────────────────────────
        self.state = "menu"

        # ── Gerenciador de fases ──────────────────────────────────────
        self.lm = LevelManager()

        # ── Sprites de fundo compartilhados ──────────────────────────
        self.menu_bg = Sprite("sprites/wallpaper/start.png")
        self.game_bg = Sprite("sprites/wallpaper/level/lvl1.png")

        # ── Botões do menu principal ──────────────────────────────────
        self.btn_start = Button("sprites/button/start.png",   window, 575, 200)
        self.btn_options = Button("sprites/button/options.png", window, 575, 400)
        self.btn_exit = Button("sprites/button/exit.png",    window, 575, 600)

        # ── Botões de dificuldade ─────────────────────────────────────
        self.btn_easy = Button("sprites/button/easy.png",   window, 575, 200)
        self.btn_normal = Button("sprites/button/normal.png", window, 575, 400)
        self.btn_hard = Button("sprites/button/hard.png",   window, 575, 600)

        # ── Seleção de fases ──────────────────────────────────────────
        self.level_select = LevelSelect(window, self.lm, self.menu_bg)

        # ── Fase e transição ativos ────────
        self._level = None          # instância de _Level1 ou LevelPlaceholder
        self._transition = None     # instância de Transition

    # ─────────────────────────────────────────────────────────────────
    # Loop principal
    # ─────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self.dt = dt

        match self.state:
            case "menu":
                self._update_menu()
            case "options":
                self._update_options()
            case "level_select":
                self._update_level_select()
            case "playing":
                self._update_playing(dt)
            case "transition":
                self._update_transition(dt)

    def draw(self):
        match self.state:
            case "menu":
                self._draw_menu()
            case "options":
                self._draw_options()
            case "level_select":
                self.level_select.draw()
            case "playing":
                self._level.draw()
            case "transition":
                self._transition.draw(self.game_bg)

    # ─────────────────────────────────────────────────────────────────
    # Menu principal
    # ─────────────────────────────────────────────────────────────────

    def _update_menu(self):
        if self.btn_start.clicked(self.window):
            self._enter_level_select()

        elif self.btn_options.clicked(self.window):
            self.state = "options"

        elif self.btn_exit.clicked(self.window):
            self.window.close()

    def _draw_menu(self):
        self.menu_bg.draw()
        self.btn_start.draw()
        self.btn_options.draw()
        self.btn_exit.draw()

    # ─────────────────────────────────────────────────────────────────
    # Opções
    # ─────────────────────────────────────────────────────────────────

    def _update_options(self):
        if (self.btn_easy.clicked(self.window) or
                self.btn_normal.clicked(self.window) or
                self.btn_hard.clicked(self.window)):
            self.state = "menu"

        if self.keyboard.key_pressed("ESC"):
            self.state = "menu"

    def _draw_options(self):
        self.menu_bg.draw()
        self.btn_easy.draw()
        self.btn_normal.draw()
        self.btn_hard.draw()

    # ─────────────────────────────────────────────────────────────────
    # Seleção de fases
    # ─────────────────────────────────────────────────────────────────

    def _enter_level_select(self):
        """Atualiza os dados e entra na tela de seleção."""
        self.level_select.refresh()
        self.state = "level_select"

    def _update_level_select(self):
        result = self.level_select.update(self.window.mouse, self.dt)

        if result == "back":
            self.state = "menu"

        elif isinstance(result, int):
            # Jogador escolheu a fase `result`
            self._start_level(result)

    # ─────────────────────────────────────────────────────────────────
    # Instanciar e iniciar uma fase
    # ─────────────────────────────────────────────────────────────────

    def _start_level(self, level_num: int):
        """Instancia a fase correta e entra no estado 'playing'."""
        self.lm.current_level = level_num

        if level_num == 1:
            self._level = _Level1(self.window)
        else:
            self._level = LevelPlaceholder(self.window, level_num)

        self.state = "playing"

    # ─────────────────────────────────────────────────────────────────
    # Jogo em execução
    # ─────────────────────────────────────────────────────────────────

    def _update_playing(self, dt: float):
        result = self._level.update(self.keyboard, dt)

        if result is None:
            return

        if result == "menu":
            self.state = "menu"

        elif result == "win":
            self._on_win()

        elif result == "lose":
            self._on_lose()

    def _on_win(self):
        current = self.lm.current_level
        self.lm.unlock_next()           # persiste o desbloqueio
        next_lv = current + 1

        self._transition = Transition(
            self.window,
            kind="win",
            current_level=current,
            next_level=next_lv,
            total_levels=self.lm.total_levels
        )
        self.state = "transition"

    def _on_lose(self):
        self._transition = Transition(
            self.window,
            kind="lose",
            current_level=self.lm.current_level,
            next_level=self.lm.current_level,
            total_levels=self.lm.total_levels
        )
        self.state = "transition"

    # ─────────────────────────────────────────────────────────────────
    # Transição entre fases
    # ─────────────────────────────────────────────────────────────────

    def _update_transition(self, dt: float):
        result = self._transition.update(dt)

        if result is None:
            return

        if result == "next":
            # Avança para a próxima fase
            advanced = self.lm.advance()
            if advanced:
                self._start_level(self.lm.current_level)
            else:
                # Fim do jogo: todas as fases completadas
                self.state = "menu"

        elif result == "menu":
            self.state = "menu"
