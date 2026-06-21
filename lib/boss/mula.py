"""
mula.py  -  Boss Mula Sem Cabeca
---------------------------------
Comportamento:
  Fase 1 (hp 100-51): idle na direita, atira fireballs periodicamente
  Fase 2 (hp 50-0):   ataque mais rapido + carrega e dispara SuperFireball

Estados: idle | attack | charge | hit | death
"""
import pygame
from random import choice
from os import listdir
from pplay.sprite import Sprite
from lib.boss.boss import Boss
from lib.boss.fireball import Fireball, SuperFireball


# Posicao fixa da Mula (direita da tela)
MULA_X = 1550
MULA_Y = 400   # ajuste conforme o sprite e o floor do level2


class Mula(Boss):

    def __init__(self, window):
        super().__init__(
            "sprites/boss/mula/idle/idle1.png",
            window, MULA_X, MULA_Y, 100
        )
        self.window = window

        # ── Animacoes ────────────────────────────────────────────────
        self.idle_frames     = self._load("sprites/boss/mula/idle")
        self.hit_frames      = self._load("sprites/boss/mula/hit")
        self.death_frames    = self._load("sprites/boss/mula/death")
        self.attack1_frames  = self._load("sprites/boss/mula/attack/fase_1")
        self.attack2_frames  = self._load("sprites/boss/mula/attack/fase_2")

        self.current_animation = self.idle_frames
        self.frame             = 0
        self.anim_timer        = 0.0
        self.anim_speed        = 0.12

        # ── Projeteis ────────────────────────────────────────────────
        self.fireballs       = []   # Fireball (pequenas)
        self.super_fireballs = []   # SuperFireball (grandes)

        # ── Timers de ataque ─────────────────────────────────────────
        # Fase 1: fireball a cada 2.5s
        self.fb_timer    = 0.0
        self.fb_cooldown = 2.5

        # Fase 2: fireball a cada 1.5s
        self.fb_cooldown_p2 = 1.5

        # Super fireball: carrega por 1.5s antes de disparar
        self.sfb_timer        = 0.0
        self.sfb_cooldown     = 6.0    # intervalo entre super-ataques
        self.charging         = False  # True durante o carregamento
        self.charge_timer     = 0.0
        self.charge_duration  = 1.5    # tempo de "aviso" antes de disparar
        self._charge_corridor = None   # corredor escolhido

        # ── Estado ───────────────────────────────────────────────────
        self.state    = "idle"
        self.dead     = False

        self.hit_timer    = 0.0
        self.hit_duration = 0.3

        # ── Animacao de ataque ────────────────────────────────────────
        self._attacking       = False
        self._attack_frame_done = False

    # =========================================================
    # HELPERS
    # =========================================================

    def _load(self, path):
        files = sorted(f for f in listdir(path) if f.endswith(".png"))
        return [Sprite(f"{path}/{f}") for f in files]

    def _is_phase2(self):
        return self.hp <= 50

    # =========================================================
    # ANIMACAO
    # =========================================================

    def animate(self, dt):
        self.anim_timer += dt
        if self.anim_timer < self.anim_speed:
            return
        self.anim_timer = 0
        self.frame += 1

        anim = self.current_animation
        if self.state == "death":
            if self.frame >= len(anim):
                self.frame = len(anim) - 1
            return

        # detecta fim do ciclo de ataque
        if self._attacking and self.frame >= len(anim):
            self.frame      = 0
            self._attacking = False
            self.state      = "idle"

        if self.frame >= len(anim):
            self.frame = 0

        old_x, old_y       = self.sprite.x, self.sprite.y
        self.sprite         = anim[self.frame]
        self.sprite.x, self.sprite.y = old_x, old_y

    # =========================================================
    # ATAQUES
    # =========================================================

    def _shoot_fireball(self, player):
        """Dispara uma fireball pequena na altura atual do jogador."""
        fb = Fireball(
            x        = self.sprite.x,
            player_y = player.sprite.y + player.sprite.height / 2,
            window   = self.window
        )
        self.fireballs.append(fb)
        self._start_attack(phase=1)

    def _start_super_charge(self):
        """Inicia o carregamento da super fireball — escolhe o corredor."""
        self.charging         = True
        self.charge_timer     = 0.0
        self._charge_corridor = choice(["chao", "meio", "topo"])
        self.state            = "charge"
        self._start_attack(phase=2)

    def _shoot_super_fireball(self):
        """Dispara a super fireball no corredor escolhido."""
        sfb = SuperFireball(
            x        = self.sprite.x,
            corridor = self._charge_corridor,
            window   = self.window
        )
        self.super_fireballs.append(sfb)
        self.charging = False
        self.state    = "idle"

    def _start_attack(self, phase: int):
        self._attacking = True
        self.frame      = 0
        self.anim_timer = 0
        self.current_animation = (
            self.attack1_frames if phase == 1 else self.attack2_frames
        )
        self.state = "attack"

    # =========================================================
    # DANO
    # =========================================================

    def check_bullets(self, player):
        """Checa balas do player contra Mula e contra fireballs."""
        for bullet in player.bullets[:]:
            hit_something = False

            # acertou a Mula
            if self.sprite.collided(bullet.sprite):
                self.take_damage(1)
                self.hit_timer = self.hit_duration
                player.bullets.remove(bullet)
                continue

            # acertou uma fireball pequena
            for fb in self.fireballs[:]:
                if not fb.dead and fb.sprite.collided(bullet.sprite):
                    destroyed = fb.take_hit()
                    player.bullets.remove(bullet)
                    if destroyed:
                        self.fireballs.remove(fb)
                    hit_something = True
                    break

    def take_damage(self, damage):
        if self.dead:
            return
        self.hp -= damage
        self.state = "hit"
        if self.hp <= 0:
            self.hp    = 0
            self.dead  = True
            self.state = "death"
            self.frame = 0
            self.current_animation = self.death_frames
            self.fireballs.clear()
            self.super_fireballs.clear()

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self, dt, player):
        if self.dead:
            self.current_animation = self.death_frames
            self.animate(dt)
            return

        phase2 = self._is_phase2()
        cooldown = self.fb_cooldown_p2 if phase2 else self.fb_cooldown

        # ── Fireball pequena ─────────────────────────────────────────
        if not self.charging:
            self.fb_timer += dt
            if self.fb_timer >= cooldown:
                self.fb_timer = 0.0
                self._shoot_fireball(player)

        # ── Super fireball (fase 2) ───────────────────────────────────
        if phase2:
            if not self.charging:
                self.sfb_timer += dt
                if self.sfb_timer >= self.sfb_cooldown:
                    self.sfb_timer = 0.0
                    self._start_super_charge()
            else:
                # carregando: exibe aviso e dispara apos charge_duration
                self.charge_timer += dt
                if self.charge_timer >= self.charge_duration:
                    self._shoot_super_fireball()

        # ── Hit ───────────────────────────────────────────────────────
        if self.hit_timer > 0:
            self.hit_timer -= dt
            if not self._attacking:
                self.current_animation = self.hit_frames
                self.state             = "hit"
        elif not self._attacking and not self.charging:
            self.current_animation = self.idle_frames
            if self.state not in ("attack", "charge"):
                self.state = "idle"

        # ── Update projeteis ─────────────────────────────────────────
        for fb in self.fireballs[:]:
            fb.update(dt)
            if fb.collides_with_player(player):
                player.take_damage(1)
                self.fireballs.remove(fb)
            elif fb.is_off_screen() or fb.dead:
                if fb in self.fireballs:
                    self.fireballs.remove(fb)

        for sfb in self.super_fireballs[:]:
            sfb.update(dt)
            if sfb.collides_with_player(player):
                player.take_damage(2)         # 2 coracoes de dano
                self.super_fireballs.remove(sfb)
            elif sfb.is_off_screen():
                self.super_fireballs.remove(sfb)

        # ── Balas do player ──────────────────────────────────────────
        self.check_bullets(player)

        self.animate(dt)

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self):
        self.sprite.draw()
        self.draw_hp_bar()

        # aviso visual do corredor alvo durante o carregamento
        if self.charging and self._charge_corridor:
            self._draw_charge_warning()

        for fb in self.fireballs:
            fb.draw()
        for sfb in self.super_fireballs:
            sfb.draw()

    def _draw_charge_warning(self):
        """Destaca o corredor que sera atacado durante o carregamento."""
        corridor_label = {
            "chao": "CHAO",
            "meio": "MEIO",
            "topo": "TOPO",
        }
        y_map = {
            "chao": SuperFireball.CORRIDOR_Y["chao"],
            "meio": SuperFireball.CORRIDOR_Y["meio"],
            "topo": SuperFireball.CORRIDOR_Y["topo"],
        }
        label = corridor_label.get(self._charge_corridor, "")
        cy    = y_map.get(self._charge_corridor, 500)

        # linha de aviso desenhada com blocos
        surf = pygame.display.get_surface()
        if surf:
            pygame.draw.line(
                surf,
                (255, 80, 0),
                (0,   cy),
                (self.sprite.x, cy),
                3
            )

        self.window.draw_text(
            f"! {label} !",
            20, cy - 30,
            size=28,
            color=(255, 120, 0)
        )
