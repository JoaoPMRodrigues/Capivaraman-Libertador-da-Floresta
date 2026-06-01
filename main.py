from pplay.window import *
from lib.game import *
from rich.traceback import install
install()

window = Window(1500, 1000)
window.set_title("Capivaraman - O Libertador da Floresta")

game = Game(window)

while True:

    dt = window.delta_time()

    game.update(dt)
    game.draw()

    window.update()
