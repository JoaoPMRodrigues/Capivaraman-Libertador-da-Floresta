from pplay.sprite import Sprite
from pplay.mouse import Mouse
from lib.level_manager import LevelManager


# ── Caminhos ──────────────────────────────────────────────────────────────────

_BRIGHT = "sprites/bosses/select/bright"
_DARK = "sprites/bosses/select/dark"

_SPRITE_FILES = {
    1: "1_saci.png",
    2: "3_mula.png",
    3: "5_corpo_seco.png",
}

_BOSS_NAMES = {
    1: "Saci",
    2: "Mula Sem Cabeca",
    3: "Corpo Seco",
}

_LEVEL_SUBTITLES = {
    1: "Floresta Primordial",
    2: "Trilha das Brasas",
    3: "Dominio do Caos",
}

# ── Layout ────────────────────────────────────────────────────────────────────

# Distância horizontal entre os centros dos cards
_CARD_GAP_X = 250

# Posição Y do centro dos cards (ajuste conforme fundo)
_CARDS_CY = 520

# Quanto o card sobe ao fazer hover (em pixels)
_HOVER_LIFT = 12

# ── Cores de texto ────────────────────────────────────────────────────────────

_COLOR_UNLOCKED = (255, 220, 60)     # dourado
_COLOR_HOVER = (255, 255, 200)    # branco quente
_COLOR_COMPLETED = (100, 255, 140)    # verde
_COLOR_LOCKED = (80, 80, 80)       # cinza escuro


# ─────────────────────────────────────────────────────────────────────────────

class _Card:

    def __init__(self, level_num: int, cx: int, cy: int,
                 spr_bright: Sprite, spr_dark: Sprite,
                 unlocked: bool):
        self.level_num = level_num
        self.cx = cx
        self.cy = cy
        self.spr_bright = spr_bright
        self.spr_dark = spr_dark
        self.unlocked = unlocked
        self._hovered = False

        # Timer de animação de hover (0.0 → 1.0)
        self._hover_t = 0.0

    # ------------------------------------------------------------------

    @property
    def _spr(self) -> Sprite:
        return self.spr_bright if self.unlocked else self.spr_dark

    def _hitbox(self):
        s = self._spr
        return (self.cx - s.width // 2,
                self.cy - s.height // 2,
                s.width, s.height)

    def contains(self, mx: int, my: int) -> bool:
        x, y, w, h = self._hitbox()
        return x <= mx <= x + w and y <= my <= y + h

    def set_hovered(self, state: bool):
        self._hovered = state

    def is_hovered(self) -> bool:
        return self._hovered

    # ------------------------------------------------------------------

    def update_anim(self, dt: float):
        target = 1.0 if (self._hovered and self.unlocked) else 0.0
        speed = 8.0
        self._hover_t += (target - self._hover_t) * speed * dt
        self._hover_t = max(0.0, min(1.0, self._hover_t))

    # ------------------------------------------------------------------

    def draw(self, window, completed: bool, dt: float):
        self.update_anim(dt)

        spr = self._spr
        lift = int(_HOVER_LIFT * self._hover_t)

        draw_x = self.cx - spr.width // 2
        draw_y = self.cy - spr.height // 2 - lift

        spr.x = draw_x
        spr.y = draw_y
        spr.draw()

        # ── Indicador de glow no hover (anel de texto de asteriscos) ──
        if self._hover_t > 0.05 and self.unlocked:
            alpha = int(200 * self._hover_t)
            window.draw_text(
                "* * * * * * *",
                draw_x - 10,
                draw_y + spr.height + 2,
                size=14,
                color=(255, 200, 50)
            )

        # ── Rótulo do boss ────────────────────────────────────────────
        name = _BOSS_NAMES.get(self.level_num, f"Fase {self.level_num}")
        sub = _LEVEL_SUBTITLES.get(self.level_num, "")

        if not self.unlocked:
            name_color = _COLOR_LOCKED
            sub_color = _COLOR_LOCKED
        elif completed:
            name_color = _COLOR_COMPLETED
            sub_color = (60, 180, 90)
        elif self._hover_t > 0.5:
            name_color = _COLOR_HOVER
            sub_color = (200, 200, 200)
        else:
            name_color = _COLOR_UNLOCKED
            sub_color = (190, 165, 50)

        label_y = draw_y + spr.height + 18
        name_x = self.cx - len(name) * 6
        window.draw_text(name, name_x, label_y, size=20, color=name_color)

        sub_x = self.cx - len(sub) * 4
        window.draw_text(sub, sub_x, label_y + 28, size=14, color=sub_color)

        # ── Cadeado se bloqueado ──────────────────────────────────────
        if not self.unlocked:
            lock_x = self.cx - 18
            lock_y = self.cy - 24
            window.draw_text("🔒", lock_x, lock_y, size=36,
                             color=(130, 130, 130))

        # ── Check verde se completado ─────────────────────────────────
        elif completed:
            check_x = draw_x + spr.width - 32
            window.draw_text("✅", check_x, draw_y + 4,
                             size=26, color=(80, 220, 100))


# ─────────────────────────────────────────────────────────────────────────────

class LevelSelect:

    def __init__(self, window, level_manager: LevelManager, bg_sprite: Sprite):
        self.window = window
        self.lm = level_manager
        self.bg = bg_sprite
        self.dt = 0.0

        self._cards: list[_Card] = []
        self._was_pressed = False

        self._load_sprites()
        self._build_cards()

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    def _load_sprites(self):
        self._bright: dict[int, Sprite] = {}
        self._dark:   dict[int, Sprite] = {}

        for num, fname in _SPRITE_FILES.items():
            # bright
            try:
                self._bright[num] = Sprite(f"{_BRIGHT}/{fname}")
            except Exception:
                try:
                    self._bright[num] = Sprite(f"{_DARK}/{fname}")
                except Exception:
                    self._bright[num] = Sprite(
                        "sprites/boss/saci/idle_left/saci_idle1.png")

            # dark
            try:
                self._dark[num] = Sprite(f"{_DARK}/{fname}")
            except Exception:
                self._dark[num] = self._bright[num]

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_cards(self):
        total = self.lm.total_levels
        wnd_w = self.window.width
        cols = total

        total_w = (cols - 1) * _CARD_GAP_X
        start_x = (wnd_w - total_w) // 2

        self._cards.clear()
        for i in range(total):
            cx = start_x + i * _CARD_GAP_X
            cy = _CARDS_CY
            num = i + 1

            self._cards.append(_Card(
                level_num=num,
                cx=cx,
                cy=cy,
                spr_bright=self._bright[num],
                spr_dark=self._dark[num],
                unlocked=self.lm.is_unlocked(num),
            ))

    def refresh(self):
        for card in self._cards:
            card.unlocked = self.lm.is_unlocked(card.level_num)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, mouse: Mouse, dt: float = 0.016):
        self.dt = dt
        mx, my = mouse.get_position()
        pressed = mouse.button_pressed(1)

        for card in self._cards:
            card.set_hovered(card.contains(mx, my))

        back_hovered = (10 <= mx <= 200 and 10 <= my <= 60)

        if pressed and not self._was_pressed:
            self._was_pressed = True

            if back_hovered:
                return "back"

            for card in self._cards:
                if card.contains(mx, my) and card.unlocked:
                    return card.level_num

        if not pressed:
            self._was_pressed = False

        return None

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self):
        w = self.window
        dt = self.dt

        self.bg.draw()

        # ── Título ───────────────────────────────────────────────────
        title = "ESCOLHA SEU DESAFIO"
        title_x = w.width // 2 - len(title) * 15
        w.draw_text(title, title_x, 38, size=48, color=(255, 215, 50))

        # ── Subtítulo ────────────────────────────────────────────────
        sub = "Derrote os bosses para liberar as proximas fases"
        sub_x = w.width // 2 - len(sub) * 5
        w.draw_text(sub, sub_x, 100, size=18, color=(180, 155, 70))

        # ── Botão Voltar ──────────────────────────────────────────────
        mx, my = w.mouse.get_position()
        back_hovered = (10 <= mx <= 200 and 10 <= my <= 60)
        back_color = (255, 255, 120) if back_hovered else (170, 170, 170)
        w.draw_text("< Voltar", 20, 15, size=28, color=back_color)

        # ── Cards ─────────────────────────────────────────────────────
        for card in self._cards:
            completed = card.level_num < self.lm.max_unlocked
            card.draw(w, completed, dt)

        # ── Dica de rodapé (hover) ────────────────────────────────────
        for card in self._cards:
            if card.is_hovered():
                if card.unlocked:
                    hint = "Clique para jogar!"
                    hint_color = (255, 255, 160)
                else:
                    hint = "Complete a fase anterior para desbloquear"
                    hint_color = (180, 90, 90)
                hint_x = w.width // 2 - len(hint) * 6
                w.draw_text(hint, hint_x, w.height - 48,
                            size=22, color=hint_color)
                break
