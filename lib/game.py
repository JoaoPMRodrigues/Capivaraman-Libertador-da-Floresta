from pplay.sprite import *
from pplay.keyboard import *

from lib.button import *
from lib.player import *


class Game:

    def __init__(self, window):

        self.window = window
        self.keyboard = Keyboard()

        self.state = "menu"

        # =====================
        # BACKGROUNDS
        # =====================

        self.menu_bg = Sprite("sprites/wallpaper/start.png")

        self.game_bg = Sprite(
            "sprites/wallpaper/level/lvl1.png"
        )

        # =====================
        # MENU BUTTONS
        # =====================

        self.start = Button(
            "sprites/button/start.png",
            window,
            575,
            200
        )

        self.options = Button(
            "sprites/button/options.png",
            window,
            575,
            400
        )

        self.exit = Button(
            "sprites/button/exit.png",
            window,
            575,
            600
        )

        # =====================
        # OPTIONS BUTTONS
        # =====================

        self.easy = Button(
            "sprites/button/easy.png",
            window,
            575,
            200
        )

        self.normal = Button(
            "sprites/button/normal.png",
            window,
            575,
            400
        )

        self.hard = Button(
            "sprites/button/hard.png",
            window,
            575,
            600
        )

        # =====================
        # PLAYER
        # =====================

        self.player = Player(window)

        # =====================
        # FPS
        # =====================

        self.cooldown = 0.3
        self.fps = 0

    # ====================================
    # UPDATE PRINCIPAL
    # ====================================

    def update(self, dt):

        if self.state == "menu":
            self.update_menu()

        elif self.state == "game":
            self.update_game(dt)

        elif self.state == "options":
            self.update_options()

    # ====================================
    # DRAW PRINCIPAL
    # ====================================

    def draw(self):

        self.window.set_background_color((0, 0, 0))

        if self.state == "menu":

            self.menu_bg.draw()

            self.start.draw()
            self.options.draw()
            self.exit.draw()

        elif self.state == "game":

            self.game_bg.draw()

            self.player.draw()

        elif self.state == "options":

            self.menu_bg.draw()

            self.easy.draw()
            self.normal.draw()
            self.hard.draw()

        self.show_fps()

    # ====================================
    # MENU
    # ====================================

    def update_menu(self):

        if self.start.clicked(self.window):
            self.state = "game"

        elif self.options.clicked(self.window):
            self.state = "options"

        elif self.exit.clicked(self.window):
            self.window.close()

    # ====================================
    # GAME
    # ====================================

    def update_game(self, dt):

        self.player.update(
            self.window,
            self.keyboard,
            dt
        )

        if self.keyboard.key_pressed("ESC"):
            self.state = "menu"

    # ====================================
    # OPTIONS
    # ====================================

    def update_options(self):

        if self.easy.clicked(self.window):
            self.state = "menu"

        elif self.normal.clicked(self.window):
            self.state = "menu"

        elif self.hard.clicked(self.window):
            self.state = "menu"

        if self.keyboard.key_pressed("ESC"):
            self.state = "menu"

    # ====================================
    # FPS
    # ====================================

    def show_fps(self):

        dt = self.window.delta_time()

        self.cooldown -= dt

        if self.cooldown < 0:

            self.fps = int(1 / dt) if dt > 0 else 0

            self.cooldown = 0.3

        self.window.draw_text(
            f"FPS: {self.fps}",
            10,
            10,
            size=25,
            color=(255, 255, 255)
        )
