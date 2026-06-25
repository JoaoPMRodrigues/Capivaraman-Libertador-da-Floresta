from pplay.sprite import *
from abc import ABC
from lib.utils import resource_path
from os import listdir


class Entity(ABC):
    def __init__(self, path, window, x=None, y=None):
        self.sprite = Sprite(path)
        self.sprite.x = x
        self.sprite.y = y
        self.window = window
        if x == None:
            self.sprite.x = window.width/2+self.sprite.width/2
        if y == None:
            self.sprite.y = window.height/2+self.sprite.height/2

    def draw(self):
        self.sprite.draw()

    def update(self):
        pass

    def _load_frames(self, path):
        real_path = resource_path(path)
        try:
            files = sorted(f for f in listdir(real_path) if f.endswith(".png"))
            return [Sprite(f"{path}/{f}") for f in files]
        except FileNotFoundError:
            return []
