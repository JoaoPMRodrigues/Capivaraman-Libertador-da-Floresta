from pplay.sprite import *
from pplay.mouse import *
from lib.entity import *


class Button(Entity):
    def __init__(self, imagem, window, x, y):
        super().__init__(imagem, window, x, y)

        self.was_pressed = False

    def clicked(self, window):
        mouse = window.mouse

        hovering = mouse.is_over_object(self.sprite)
        pressed = mouse.button_pressed(1)

        # Detecta clique único
        if hovering and pressed and not self.was_pressed:
            self.was_pressed = True
            return True

        # Reset quando soltar botão
        if not pressed:
            self.was_pressed = False

        return False

    def update(self, window):
        return self.clicked(window)
