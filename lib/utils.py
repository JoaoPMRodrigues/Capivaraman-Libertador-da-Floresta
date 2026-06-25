import os
import sys

# Criado exclusivamente para transformar o jogo em um executável


def resource_path(path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, path)
    return path
