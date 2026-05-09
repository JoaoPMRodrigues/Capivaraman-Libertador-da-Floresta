from pplay.sprite import *
from pplay.mouse import *
from lib.entity import *


class Button(Entity):
    def __init__(self, imagem, window, x, y):
        super().__init__(imagem, window, x, y)

    def clicked(self, window):
        mouse = window.mouse
        return mouse.is_over_object(self.sprite) and mouse.button_pressed(1)

    def update(self, window):
        if self.clicked(window):
            return True
        return False
