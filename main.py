from pplay.window import *
from lib.game import *

window = Window(1500, 1000)
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
