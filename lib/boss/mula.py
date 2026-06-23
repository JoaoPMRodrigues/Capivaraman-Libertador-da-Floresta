import pygame
from random import choice
from os import listdir
from os.path import isfile
from pplay.sprite import Sprite
from lib.boss.boss import Boss
from lib.boss.fireball import Fireball, SuperFireball


# ── Posição fixa da Mula (direita da tela) ─────────────────────────────────
MULA_X = 1550
MULA_Y = 535


class Mula(Boss):

    def __init__(self, window):
        super().__init__(
            "sprites/boss/mula/idle/idle1.png",
            window, MULA_X, MULA_Y, 100
        )
        self.window = window

        # ── Animações ────────────────────────────────────────────────────────
        self.idle_frames = self._load("sprites/boss/mula/idle")
        self.hit_frames = self._load("sprites/boss/mula/hit")
        self.death_frames = self._load("sprites/boss/mula/death")
        self.attack1_frames = self._load("sprites/boss/mula/attack/fase_1")
        self.attack2_frames = self._load("sprites/boss/mula/attack/fase_2")

        self.current_animation = self.idle_frames
        self.frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.12

        # ── Projéteis ────────────────────────────────────────────────────────
        self.fireballs = []
        self.super_fireballs = []

        # ── Timers de ataque ─────────────────────────────────────────────────
        self.fb_timer = 0.0
        self.fb_cooldown = 2.5   # fase 1
        self.fb_cooldown_p2 = 1.5   # fase 2

        self.sfb_timer = 0.0
        self.sfb_cooldown = 6.0
        self.charging = False
        self.charge_timer = 0.0
        self.charge_duration = 1.5
        self._charge_corridor = None

        # ── Estado ───────────────────────────────────────────────────────────
        self.state = "idle"
        self.dead = False

        self.hit_timer = 0.0
        self.hit_duration = 0.3

        self._attacking = False
        self._attack_frame_done = False

    # =========================================================
    # HELPERS
    # =========================================================

    def _load(self, path: str):
        """Carrega frames de animação de uma pasta. Retorna lista com 1 sprite
        de fallback caso a pasta não exista ou esteja vazia."""
        try:
            files = sorted(
                f for f in listdir(path)
                if f.endswith(".png") and isfile(f"{path}/{f}")
            )
            if not files:
                raise FileNotFoundError
            return [Sprite(f"{path}/{f}") for f in files]
        except (FileNotFoundError, OSError):
            # Fallback: reutiliza o sprite base
            return [self.sprite]

    def _is_phase2(self) -> bool:
        return self.hp <= 75

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

        if self.state == "death":
            if self.frame >= len(anim):
                self.frame = len(anim) - 1
            self._apply_frame(anim)
            return

        if self._attacking and self.frame >= len(anim):
            self.frame = 0
            self._attacking = False
            self.state = "idle"

        if self.frame >= len(anim):
            self.frame = 0

        self._apply_frame(anim)

    def _apply_frame(self, anim):
        old_x, old_y = self.sprite.x, self.sprite.y
        self.sprite = anim[self.frame]
        self.sprite.x = old_x
        self.sprite.y = old_y

    # =========================================================
    # ATAQUES
    # =========================================================

    def _shoot_fireball(self, player):

        centro_y = player.sprite.y + player.sprite.height / 2
        espacamento = 80

        for offset in (-espacamento, 0, espacamento):
            fb = Fireball(
                x=self.sprite.x,
                player_y=centro_y + offset,
                window=self.window
            )
            self.fireballs.append(fb)

        self._start_attack(phase=1)

    def _start_super_charge(self):
        self.charging = True
        self.charge_timer = 0.0
        self._charge_corridor = choice(["chao", "meio", "topo"])
        self.state = "charge"
        self._start_attack(phase=2)

    def _shoot_super_fireball(self):
        sfb = SuperFireball(
            x=self.sprite.x,
            corridor=self._charge_corridor,
            window=self.window
        )
        self.super_fireballs.append(sfb)
        self.charging = False
        self.state = "idle"

    def _start_attack(self, phase: int):
        self._attacking = True
        self.frame = 0
        self.anim_timer = 0
        self.current_animation = (
            self.attack1_frames if phase == 1 else self.attack2_frames
        )
        self.state = "attack"

    # =========================================================
    # DANO
    # =========================================================

    def check_bullets(self, player):
        """Checa balas do player contra a Mula e contra fireballs."""
        for bullet in player.bullets[:]:
            removed = False

            # ── Acertou a Mula ───────────────────────────────────────────────
            if self.sprite.collided(bullet.sprite):
                self.take_damage(1)
                self.hit_timer = self.hit_duration
                player.bullets.remove(bullet)
                removed = True
                continue

            if removed:
                continue

            # ── Acertou uma fireball pequena ─────────────────────────────────
            b_rect = pygame.Rect(
                int(bullet.sprite.x), int(bullet.sprite.y),
                int(bullet.sprite.width), int(bullet.sprite.height)
            )
            for fb in self.fireballs[:]:
                if not fb.dead and fb.sprite.collided(b_rect):
                    destroyed = fb.take_hit()
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    if destroyed and fb in self.fireballs:
                        self.fireballs.remove(fb)
                    removed = True
                    break

    def take_damage(self, damage: int):
        if self.dead:
            return
        self.hp -= damage
        self.state = "hit"
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.state = "death"
            self.frame = 0
            self.current_animation = self.death_frames
            self.fireballs.clear()
            self.super_fireballs.clear()

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self, dt: float, player):
        if self.dead:
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        phase2 = self._is_phase2()
        cooldown = self.fb_cooldown_p2 if phase2 else self.fb_cooldown

        # ── Fireball pequena ─────────────────────────────────────────────────
        if not self.charging:
            self.fb_timer += dt
            if self.fb_timer >= cooldown:
                self.fb_timer = 0.0
                self._shoot_fireball(player)

        # ── Super fireball (fase 2) ──────────────────────────────────────────
        if phase2:
            if not self.charging:
                self.sfb_timer += dt
                if self.sfb_timer >= self.sfb_cooldown:
                    self.sfb_timer = 0.0
                    self._start_super_charge()
            else:
                self.charge_timer += dt
                if self.charge_timer >= self.charge_duration:
                    self._shoot_super_fireball()

        # ── Hit ──────────────────────────────────────────────────────────────
        if self.hit_timer > 0:
            self.hit_timer -= dt
            if not self._attacking:
                self.current_animation = self.hit_frames
                self.state = "hit"
        elif not self._attacking and not self.charging:
            self.current_animation = self.idle_frames
            if self.state not in ("attack", "charge"):
                self.state = "idle"

        # ── Update projéteis ─────────────────────────────────────────────────
        for fb in self.fireballs[:]:
            fb.update(dt)
            if fb.collides_with_player(player):
                player.take_damage(Fireball.DAMAGE)
                self.fireballs.remove(fb)
            elif fb.is_off_screen() or fb.dead:
                if fb in self.fireballs:
                    self.fireballs.remove(fb)

        for sfb in self.super_fireballs[:]:
            sfb.update(dt)
            if sfb.collides_with_player(player):
                player.take_damage(SuperFireball.DAMAGE)
                self.super_fireballs.remove(sfb)
            elif sfb.is_off_screen():
                self.super_fireballs.remove(sfb)

        # ── Balas do player ──────────────────────────────────────────────────
        self.check_bullets(player)

        self.animate(dt)

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self):
        self.sprite.draw()
        self.draw_hp_bar()

        if self.charging and self._charge_corridor:
            self._draw_charge_warning()

        for fb in self.fireballs:
            fb.draw()
        for sfb in self.super_fireballs:
            sfb.draw()

    def _draw_charge_warning(self):
        """Destaca o corredor que será atacado durante o carregamento."""
        y_map = SuperFireball.CORRIDOR_Y
        label_map = {"chao": "CHÃO", "meio": "MEIO", "topo": "TOPO"}

        label = label_map.get(self._charge_corridor, "")
        cy = y_map.get(self._charge_corridor, 500)

        surf = pygame.display.get_surface()
        if surf:
            pygame.draw.line(
                surf,
                (255, 80, 0),
                (0, cy),
                (int(self.sprite.x), cy),
                3
            )

        self.window.draw_text(
            f"! {label} !",
            20, cy - 30,
            size=28,
            color=(255, 120, 0)
        )
