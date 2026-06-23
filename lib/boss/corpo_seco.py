import pygame
from os import listdir
from os.path import isfile
from pplay.sprite import Sprite
from lib.boss.boss import Boss
from lib.boss.platform import *

# Posição inicial padrão do Corpo Seco no lado direito da tela
CORPO_SECO_X = 1450
CORPO_SECO_Y = 550  # Ajuste esta altura conforme o chão/plataforma da sua Fase 3

class CorpoSeco(Boss):

    def __init__(self, window):
        # Inicializa a classe base Boss com o frame inicial e 100 pontos de vida
        super().__init__(
            "sprites/boss/corpo-seco/idle/idle1.png",
            window, CORPO_SECO_X, CORPO_SECO_Y, 100
        )
        self.window = window

        # ── Animações ────────────────────────────────────────────────────────
        self.idle_frames = self._load("sprites/boss/corpo-seco/idle")
        self.hit_frames = self._load("sprites/boss/corpo-seco/hit")
        self.death_frames = self._load("sprites/boss/corpo-seco/death")

        self.current_animation = self.idle_frames
        self.frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.12  # Velocidade da troca de frames

        # ── Estados e Timers ─────────────────────────────────────────────────
        self.state = "idle"
        self.dead = False

        self.hit_timer = 0.0
        self.hit_duration = 0.3  # Tempo que ele fica na animação de dano

    # =========================================================
    # HELPERS
    # =========================================================

    def _load(self, path: str):
        """Carrega frames de animação de uma pasta. Retorna uma lista com o 
        sprite base de fallback caso a pasta não exista ou esteja vazia."""
        try:
            files = sorted(
                f for f in listdir(path)
                if f.endswith(".png") and isfile(f"{path}/{f}")
            )
            if not files:
                raise FileNotFoundError
            return [Sprite(f"{path}/{f}") for f in files]
        except (FileNotFoundError, OSError):
            return [self.sprite]

    # =========================================================
    # ANIMAÇÃO
    # =========================================================

    def animate(self, dt: float):
        self.anim_timer += dt
        if self.anim_timer < self.anim_speed:
            return
        self.anim_timer = 0
        self.frame += 1

        anim = self.current_animation

        # Travamento no último frame da morte
        if self.state == "death":
            if self.frame >= len(anim):
                self.frame = len(anim) - 1
            self._apply_frame(anim)
            return

        # Loop normal para idle e hit
        if self.frame >= len(anim):
            self.frame = 0

        self._apply_frame(anim)

    def _apply_frame(self, anim):
        old_x, old_y = self.sprite.x, self.sprite.y
        self.sprite = anim[self.frame]
        self.sprite.x = old_x
        self.sprite.y = old_y

    # =========================================================
    # DANO E COLISÃO
    # =========================================================

    def check_bullets(self, player):
        """Monitora e resolve colisões com os tiros disparados pelo Player."""
        for bullet in player.bullets[:]:
            if self.sprite.collided(bullet.sprite):
                self.take_damage(1)
                if bullet in player.bullets:
                    player.bullets.remove(bullet)

    def take_damage(self, damage: int):
        if self.dead:
            return

        self.hp -= damage
        self.hit_timer = self.hit_duration
        self.state = "hit"

        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.state = "death"
            self.frame = 0
            self.current_animation = self.death_frames

    # =========================================================
    # UPDATE & DRAW
    # =========================================================

    def update(self, dt: float, player):
        if self.dead:
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        # Controle da animação de Hit (Dano)
        if self.hit_timer > 0:
            self.hit_timer -= dt
            self.current_animation = self.hit_frames
            self.state = "hit"
        else:
            self.current_animation = self.idle_frames
            self.state = "idle"

        # Varre colisões com ataques do player
        self.check_bullets(player)

        # Processa ciclo de animação
        self.animate(dt)

    def draw(self):
        self.sprite.draw()
        self.draw_hp_bar()  # Reaproveita a barra de HP nativa do seu sistema base