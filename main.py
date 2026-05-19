from pplay.window import *
from pplay.sprite import *
from pplay.keyboard import *
from pplay.mouse import *
from lib.button import *
from time import sleep
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

keyboard = Keyboard()

while True:
    window.set_background_color((0, 0, 0))
    background.draw()
    dt = window.delta_time()

    if tela == "menu":
        start.draw()
        options.draw()
        exit.draw()
        if start.clicked(window):
            sleep(0.2)
            tela = "game"
        elif options.clicked(window):
            sleep(0.2)
            tela = "options"
        elif exit.clicked(window):
            sleep(0.2)
            break

    if tela == "game":
        if keyboard.key_pressed("ESC"):
            tela = "menu"

    if tela == "options":
        easy.draw()
        normal.draw()
        hard.draw()

        if easy.clicked(window):
            sleep(0.2)
            tela = "menu"
        if normal.clicked(window):
            sleep(0.2)
            tela = "menu"
        if hard.clicked(window):
            sleep(0.2)
            tela = "menu"

        if keyboard.key_pressed("ESC"):
            tela = "menu"

    window.update()
