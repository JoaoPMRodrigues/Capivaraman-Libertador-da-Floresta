import pygame
import random
from os import listdir
from os.path import isfile
from pplay.sprite import Sprite
from lib.boss.boss import Boss
from lib.boss.platform import *
from lib.boss.skull import Skull

CORPO_SECO_X = 1450
CORPO_SECO_Y = 250


class CorpoSeco(Boss):

    def __init__(self, window):
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
        self.anim_speed = 0.12

        # ── Estados e Timers ─────────────────────────────────────────────────
        self.state = "idle"
        self.dead = False

        self.hit_timer = 0.0
        self.hit_duration = 0.3

        # ── Gerenciador de Caveiras ──────────────────────────────────────────
        self.skulls = []
        self.shoot_cooldown_timer = 0.0
        self.shoot_cooldown_duration = 3.0  # Tempo entre os ataques

        # Configuração das alturas dos corredores fornecidas para a Fase 2
        self.CORRIDOR_Y = {
            "chao": 130,   # corredor do chao
            "meio": 430,   # corredor das plataformas medias
            "topo": 800,   # corredor das plataformas grandes
        }

    def _load(self, path: str):
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

    def animate(self, dt: float):
        self.anim_timer += dt
        if self.anim_timer < self.anim_speed:
            return
        self.anim_timer = 0
        self.frame += 1

        anim = self.current_animation

        if self.state == "death":
            if self.frame >= len(anim):
                self.frame = len(anim) - 1
            self._apply_frame(anim)
            return

        if self.frame >= len(anim):
            self.frame = 0

        self._apply_frame(anim)

    def _apply_frame(self, anim):
        old_x, old_y = self.sprite.x, self.sprite.y
        self.sprite = anim[self.frame]
        self.sprite.x = old_x
        self.sprite.y = old_y

    # =========================================================
    # DANO E COLISÃO (BOSS & CAVEIRAS)
    # =========================================================

    def check_bullets(self, player):
        for bullet in player.bullets[:]:
            if self.sprite.collided(bullet.sprite):
                self.take_damage(1)
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
                continue

            for skull in self.skulls[:]:
                if skull.sprite.collided(bullet.sprite):
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    skull.take_hit()
                    if skull.dead:
                        self.skulls.remove(skull)
                    break

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
            self.skulls.clear()

    # =========================================================
    # SISTEMA DE ATAQUE (FASE 1 E FASE 2)
    # =========================================================

    def _process_shooting(self, dt: float, player):
        """Gerencia o disparo periódico das caveiras se adaptando à vida atual do Boss."""
        self.shoot_cooldown_timer += dt
        if self.shoot_cooldown_timer < self.shoot_cooldown_duration:
            return

        self.shoot_cooldown_timer = 0.0
        offset_vertical = 64  # Distância de empilhamento vertical entre as caveiras

        # ── FASE 2: Vida menor ou igual a 50 ──────────────────────────────────
        if self.hp <= 70:
            # Escolhe exatamente 2 chaves/pontos diferentes da lista ["chao", "meio", "topo"]
            corredores_escolhidos = random.sample(["chao", "meio", "topo"], 2)

            for corredor in corredores_escolhidos:
                base_y = self.CORRIDOR_Y[corredor]

                # Instancia uma coluna em pé com 3 caveiras na altura selecionada
                self.skulls.append(
                    Skull(self.sprite.x, base_y - offset_vertical))
                self.skulls.append(Skull(self.sprite.x, base_y))

        # ── FASE 1: Vida maior que 60 (Comportamento padrão mirando no Player) ────
        else:
            quantidade = random.randint(1, 3)
            base_y = player.sprite.y + (player.sprite.height / 2)

            if quantidade == 1:
                self.skulls.append(Skull(self.sprite.x, base_y))
            elif quantidade == 2:
                self.skulls.append(
                    Skull(self.sprite.x, base_y - (offset_vertical / 2)))
                self.skulls.append(
                    Skull(self.sprite.x, base_y + (offset_vertical / 2)))
            elif quantidade == 3:
                self.skulls.append(
                    Skull(self.sprite.x, base_y - offset_vertical))
                self.skulls.append(Skull(self.sprite.x, base_y))
                self.skulls.append(
                    Skull(self.sprite.x, base_y + offset_vertical))

    # =========================================================
    # UPDATE & DRAW
    # =========================================================

    def update(self, dt: float, player):
        if self.dead:
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        if self.hit_timer > 0:
            self.hit_timer -= dt
            self.current_animation = self.hit_frames
            self.state = "hit"
        else:
            self.current_animation = self.idle_frames
            self.state = "idle"

        # Executa a rotina inteligente de ataque
        self._process_shooting(dt, player)

        for skull in self.skulls[:]:
            skull.update(dt)

            if skull.collides_with_player(player):
                if hasattr(player, "take_damage"):
                    player.take_damage(3)
                else:
                    player.life = 0

                player.dead = True
                skull.dead = True
                self.skulls.remove(skull)
                continue

            if skull.sprite.x < -150:
                self.skulls.remove(skull)

        self.check_bullets(player)
        self.animate(dt)

    def draw(self):
        self.sprite.draw()
        self.draw_hp_bar()

        for skull in self.skulls:
            skull.draw()
