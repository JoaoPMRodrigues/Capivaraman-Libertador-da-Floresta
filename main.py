from pplay.window import *
from pplay.sprite import *
from pplay.keyboard import *
from pplay.mouse import *
from lib.button import *
from time import sleep
from rich.traceback import install
install()

x = 1536
y = 1024
window = Window(x, y)
window.set_title("Capivaraman - O Libertador da Floresta")

background = Sprite("sprites/wallpaper/start.png", 1)

# Criando botões do menu

start = Button("sprites/button/start.png", window, 575, 200)
options = Button("sprites/button/options.png", window, 575, 400)
exit = Button("sprites/button/exit.png", window, 600, 600)
tela = "Menu"

keyboard = Keyboard()

while True:
    window.set_background_color((0, 0, 0))
    background.draw()
    dt = window.delta_time()

    if tela == "Menu":
        start.draw()
        options.draw()
        exit.draw()
        if start.clicked(window):
            tela = "Game"
        elif options.clicked(window):
            tela = "Options"
        elif exit.clicked(window):
            break

    if tela == "Game":
        if keyboard.key_pressed("ESC"):
            sleep(0.2)
            tela = "Menu"

    if tela == "Options":
        if keyboard.key_pressed("ESC"):
            sleep(0.2)
            tela = "Menu"

    window.update()
