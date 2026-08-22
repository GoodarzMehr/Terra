"""Visual juice: explosion particles, screen shake, floating score popups."""

import math
import random

import pygame

from . import config as C


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "drag")

    def __init__(self, x, y, vx, vy, life, color, size=3, drag=2.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size = size
        self.drag = drag

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx -= self.vx * self.drag * dt
        self.vy -= self.vy * self.drag * dt

    def draw(self, surf, ox, oy):
        k = max(0.0, self.life / self.max_life)
        size = max(1, int(self.size * k))
        col = tuple(int(c * (0.4 + 0.6 * k)) for c in self.color)
        pygame.draw.circle(surf, col, (int(self.x + ox), int(self.y + oy)), size)


class ScorePopup:
    __slots__ = ("x", "y", "text", "life", "max_life", "color")

    def __init__(self, x, y, text, color, life=0.9):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = self.max_life = life

    def update(self, dt):
        self.life -= dt
        self.y -= 34 * dt

    def draw(self, surf, font, ox, oy):
        if self.life <= 0:
            return
        a = max(0.0, min(1.0, self.life / (self.max_life * 0.5)))
        img = font.render(self.text, True, self.color)
        img.set_alpha(int(255 * a))
        rect = img.get_rect(center=(int(self.x + ox), int(self.y + oy)))
        surf.blit(img, rect)


class Effects:
    """Holds particles, popups, and the screen-shake state."""

    def __init__(self):
        self.particles = []
        self.popups = []
        self.shake_t = 0.0
        self.shake_dur = 0.0
        self.shake_mag = 0.0
        self.flash_t = 0.0
        self.flash_color = (255, 255, 255)

    # -- spawning ---------------------------------------------------------
    def explosion(self, x, y, color, count=22, speed=220.0, life=0.55, size=3):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(speed * 0.25, speed)
            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp,
                         random.uniform(life * 0.5, life), color, size)
            )
        # hot white core
        for _ in range(count // 4):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(30, 90)
            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp,
                         life * 0.4, C.WHITE, 2)
            )

    def spark(self, x, y, color, count=6, speed=120.0, life=0.3):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(speed * 0.3, speed)
            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp,
                         random.uniform(life * 0.5, life), color, 2)
            )

    def popup(self, x, y, text, color):
        self.popups.append(ScorePopup(x, y, text, color))

    def shake(self, magnitude, duration):
        # keep the strongest shake currently active
        if self.shake_t <= 0 or magnitude > self.shake_mag:
            self.shake_mag = magnitude
            self.shake_dur = duration
            self.shake_t = duration

    def flash(self, color, duration=0.12):
        self.flash_color = color
        self.flash_t = duration

    # -- update / draw ----------------------------------------------------
    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        for pop in self.popups:
            pop.update(dt)
        self.popups = [p for p in self.popups if p.life > 0]
        if self.shake_t > 0:
            self.shake_t -= dt
        if self.flash_t > 0:
            self.flash_t -= dt

    def offset(self):
        if self.shake_t <= 0:
            return 0, 0
        k = self.shake_t / max(1e-6, self.shake_dur)
        m = self.shake_mag * k
        return (random.uniform(-m, m), random.uniform(-m, m))

    def draw(self, surf, ox, oy, popup_font):
        for p in self.particles:
            p.draw(surf, ox, oy)
        for pop in self.popups:
            pop.draw(surf, popup_font, ox, oy)
        if self.flash_t > 0:
            a = int(90 * (self.flash_t / 0.12))
            a = max(0, min(255, a))
            flash = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.flash_color, a))
            surf.blit(flash, (0, 0))
