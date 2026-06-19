from pplay.window import *
from lib.game import *
from rich.traceback import install
install()
# Se o código não rodar, esse comando ajuda a ver onde está o erro

window = Window(1920, 1080)
window.set_title("Capivaraman - O Libertador da Floresta")

game = Game(window)

while True:
    dt = window.delta_time()
    if dt <= 0 or dt > 0.2:
        dt = 1 / 60

    game.dt = dt
    game.update(dt)
    game.draw()
    window.update()
