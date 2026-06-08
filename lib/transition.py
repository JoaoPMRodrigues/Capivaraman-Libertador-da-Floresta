import math


# Duração padrão de cada fase da transição (em segundos)
_HOLD_TIME = 2.5     # quanto tempo a mensagem fica na tela
_FADE_TIME = 0.6     # duração do fade-in/out da mensagem


class Transition:
    def __init__(self, window, kind: str = "win",
                 current_level: int = 1, next_level: int = 2,
                 total_levels: int = 5):
        self.window = window
        self.kind = kind
        self.current_level = current_level
        self.next_level = next_level
        self.total_levels = total_levels

        self._timer = 0.0
        self._total = _FADE_TIME + _HOLD_TIME + _FADE_TIME
        self._done = False
        self._result = None

        # Textos e cores conforme o tipo
        if kind == "win":
            if current_level >= total_levels:
                # Última fase: fim do jogo
                self.kind = "end"

        self._setup_content()

    # ------------------------------------------------------------------
    # Configuração de conteúdo
    # ------------------------------------------------------------------

    def _setup_content(self):
        kind = self.kind
        if kind == "win":
            self._title = "FASE CONCLUÍDA!"
            self._title_color = (80, 255, 120)
            self._subtitle = f"Próxima: Fase {self.next_level}"
            self._subtitle_color = (200, 255, 200)
            self._result = "next"

        elif kind == "lose":
            self._title = "VOCÊ CAIU..."
            self._title_color = (255, 80, 80)
            self._subtitle = "Voltando ao menu..."
            self._subtitle_color = (255, 200, 200)
            self._result = "menu"

        elif kind == "end":
            self._title = "PARABÉNS, LIBERTADOR!"
            self._title_color = (255, 220, 50)
            self._subtitle = "Você venceu todos os chefes!"
            self._subtitle_color = (255, 255, 200)
            self._result = "menu"

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------

    def update(self, dt: float):
        self._timer += dt

        if self._timer >= self._total:
            if not self._done:
                self._done = True
                return self._result

        return None

    def draw(self, bg_sprite=None):
        w = self.window

        # Desenha fundo caso fornecido
        if bg_sprite is not None:
            bg_sprite.draw()

        # ── Calcula alpha para fade ──────────────────────────────────
        alpha = self._calc_alpha()

        # Overlay escurecido
        self._draw_overlay(alpha)

        # ── Título principal ─────────────────────────────────────────
        title_x = w.width // 2 - len(self._title) * 18
        title_y = w.height // 2 - 80

        # Sombra
        w.draw_text(self._title, title_x + 3, title_y + 3,
                    size=60, color=(0, 0, 0))
        # Texto
        w.draw_text(self._title, title_x, title_y,
                    size=60, color=self._title_color)

        # ── Subtítulo ────────────────────────────────────────────────
        sub_x = w.width // 2 - len(self._subtitle) * 10
        sub_y = w.height // 2 + 20
        w.draw_text(self._subtitle, sub_x, sub_y,
                    size=32, color=self._subtitle_color)

        # ── Indicador de progresso de fase ───────────────────────────
        if self.kind in ("win", "end"):
            self._draw_phase_dots()

        # ── Contador regressivo ───────────────────────────────────────
        remaining = max(0.0, self._total - self._timer)
        dots = "." * (int(self._timer * 2) % 4)
        w.draw_text(
            f"Aguarde{dots}",
            w.width // 2 - 70, w.height // 2 + 100,
            size=22, color=(180, 180, 180)
        )

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------

    def _calc_alpha(self) -> float:
        t = self._timer
        if t < _FADE_TIME:
            return t / _FADE_TIME
        elif t < _FADE_TIME + _HOLD_TIME:
            return 1.0
        else:
            elapsed = t - _FADE_TIME - _HOLD_TIME
            return max(0.0, 1.0 - elapsed / _FADE_TIME)

    def _draw_overlay(self, alpha: float):
        w = self.window
        # Intensidade: 0-180 de escurecimento
        dark = int(alpha * 180)
        color = (0, 0, 0) if dark > 10 else None
        if color is None:
            return

        # Cobre a tela com linhas de blocos escuros
        chars_per_line = w.width // 10 + 2
        lines = w.height // 16 + 2
        for row in range(lines):
            w.draw_text(
                "█" * chars_per_line,
                0, row * 16,
                size=10, color=(0, 0, int(dark * 0.4))
            )

    def _draw_phase_dots(self):
        w = self.window
        total = self.total_levels
        dot_size = 20
        gap = 14
        total_w = total * dot_size + (total - 1) * gap
        start_x = w.width // 2 - total_w // 2
        y = w.height // 2 + 150

        for i in range(1, total + 1):
            if i < self.current_level or (self.kind == "win" and i <= self.current_level):
                symbol = "●"
                color = (80, 220, 100)    # verde = concluída
            elif i == self.next_level and self.kind == "win":
                symbol = "○"
                color = (255, 220, 50)    # amarelo = próxima
            else:
                symbol = "○"
                color = (100, 100, 100)   # cinza = bloqueada

            x = start_x + (i - 1) * (dot_size + gap)
            w.draw_text(symbol, x, y, size=dot_size, color=color)
