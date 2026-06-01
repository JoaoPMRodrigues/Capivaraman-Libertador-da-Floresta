from lib.entity import *


class Boss(Entity):

    def __init__(
        self,
        path,
        window,
        x,
        y,
        hp
    ):

        super().__init__(
            path,
            window,
            x,
            y
        )

        self.max_hp = hp
        self.hp = hp

        self.dead = False

        self.state = "idle"

    def take_damage(self, damage):

        if self.dead:
            return

        self.hp -= damage

        self.state = "hit"

        if self.hp <= 0:

            self.hp = 0

            self.dead = True

            self.state = "death"

    def draw_hp_bar(self, window):

        largura_total = 500

        porcentagem = self.hp / self.max_hp

        largura_atual = largura_total * porcentagem

        # Fundo
        window.draw_text(
            "█" * 50,
            500,
            20,
            size=20,
            color=(80, 80, 80)
        )

        # Vida
        window.draw_text(
            "█" * int(50 * porcentagem),
            500,
            20,
            size=20,
            color=(255, 0, 0)
        )

        window.draw_text(
            f"{self.hp}/{self.max_hp}",
            490,
            50,
            size=30,
            color=(255, 255, 255)
        )
