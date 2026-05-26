from pplay.window import *
from pplay.sprite import *
from pplay.keyboard import *
from pplay.mouse import *
from lib.button import *
from lib.game import *
from lib.player import *
from rich.traceback import install
install()

x = 1500
y = 1000
window = Window(x, y)
window.set_title("Capivaraman - O Libertador da Floresta")

background = Sprite("sprites/wallpaper/start.png", 1)

# Criando botões do menu

start = Button("sprites/button/start.png", window, 575, 200)
options = Button("sprites/button/options.png", window, 575, 400)
exit = Button("sprites/button/exit.png", window, 575, 600)
tela = "menu"

# Criando botões de dificuldade

easy = Button("sprites/button/easy.png", window, 575, 200)
normal = Button("sprites/button/normal.png", window, 575, 400)
hard = Button("sprites/button/hard.png", window, 575, 600)

# Criando o player

player = Player(window)

keyboard = Keyboard()
cooldown = 0.3
fps = 0

while True:
    window.set_background_color((0, 0, 0))
    background.draw()
    dt = window.delta_time()

    if tela == "menu":
        start.draw()
        options.draw()
        exit.draw()
        if start.clicked(window):
            background = Sprite("sprites/wallpaper/level/lvl1.png")
            tela = "game"
        elif options.clicked(window):
            tela = "options"
        elif exit.clicked(window):
            break

    if tela == "game":
        background.draw()

        player.update(
            window,
            keyboard,
            dt
        )

        player.draw()
        if keyboard.key_pressed("ESC"):
            background = Sprite("sprites/wallpaper/start.png", 1)
            tela = "menu"

    if tela == "options":

        easy.draw()
        normal.draw()
        hard.draw()

        if easy.clicked(window):
            tela = "menu"
        if normal.clicked(window):
            tela = "menu"
        if hard.clicked(window):
            tela = "menu"

        if keyboard.key_pressed("ESC"):
            background = Sprite("sprites/wallpaper/start.png", 1)
            tela = "menu"

    cooldown, fps = show_fps(window, cooldown, dt, fps)
    window.update()
