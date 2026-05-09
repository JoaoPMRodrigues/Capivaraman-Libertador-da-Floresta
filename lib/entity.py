from pplay.sprite import *


class Entity:
    def __init__(self, path, window, x=None, y=None):
        self.sprite = Sprite(path)
        self.sprite.x = x
        self.sprite.y = y
        if x == None:
            self.sprite.x = window.width/2+self.sprite.width/2
        if y == None:
            self.sprite.y = window.height/2+self.sprite.height/2

    def draw(self):
        self.sprite.draw()
