from pplay.sprite import *
from pplay.mouse import *
from lib.entity import *


class Button(Entity):
    was_pressed = False

    def __init__(self, path, window, x, y):
        super().__init__(path, window, x, y)
        self.sprite.x = window.width/2 - self.sprite.width/2

    def clicked(self):
        mouse = self.window.mouse
        hovering = mouse.is_over_object(self.sprite)
        pressed = mouse.button_pressed(1)  # botão esquerdo

        if hovering and pressed and not Button.was_pressed:
            Button.was_pressed = True
            return True

        # Reset do estado quando o botão é solto
        if not pressed:
            Button.was_pressed = False

        return False

    def update(self):
        return self.clicked(self.window)
