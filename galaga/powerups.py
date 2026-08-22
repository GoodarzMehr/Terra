"""Power-up drops: falling pickups and their timed effects."""

import math
import random

import pygame

from . import config as C

# (kind, weight, color, label char)
TABLE = [
    ("triple", 30, C.YELLOW, "3"),
    ("rapid", 30, C.MAGENTA, "R"),
    ("shield", 25, C.CYAN, "S"),
    ("life", 15, C.PINK, "+"),
]


class Powerup:
    __slots__ = ("kind", "x", "y", "t", "alive", "color", "label")

    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.t = 0.0
        self.alive = True
        for k, _w, c, lab in TABLE:
            if k == kind:
                self.color = c
                self.label = lab
                break

    def update(self, dt):
        self.t += dt
        self.y += C.POWERUP_FALL_SPEED * dt
        self.x += math.sin(self.t * 2.0) * 30 * dt  # gentle sway
        if self.y > C.HEIGHT + 20:
            self.alive = False

    def rect(self):
        s = C.POWERUP_W
        return pygame.Rect(int(self.x - s / 2), int(self.y - s / 2), s, s)

    def draw(self, surf, font, ox, oy):
        pulse = 0.6 + 0.4 * math.sin(self.t * 6.0)
        x, y = int(self.x + ox), int(self.y + oy)
        # glow
        glow = pygame.Surface((C.POWERUP_W * 2, C.POWERUP_W * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, int(60 * pulse)), (C.POWERUP_W, C.POWERUP_W), C.POWERUP_W)
        surf.blit(glow, (x - C.POWERUP_W, y - C.POWERUP_W))
        # capsule
        pygame.draw.rect(surf, self.color, (x - 10, y - 10, 20, 20), border_radius=6)
        pygame.draw.rect(surf, C.WHITE, (x - 10, y - 10, 20, 20), 2, border_radius=6)
        img = font.render(self.label, True, C.WHITE)
        surf.blit(img, img.get_rect(center=(x, y)))


class PowerupManager:
    def __init__(self):
        self.pickups = []

    def reset(self):
        self.pickups.clear()

    def maybe_drop(self, x, y, etype):
        """Roll for a drop from a kill. Bosses always drop."""
        chance = C.POWERUP_BOSS_DROP if etype == "boss" else C.POWERUP_DROP_CHANCE
        if random.random() > chance:
            return
        kind = self._roll_kind()
        self.pickups.append(Powerup(kind, x, y))

    def _roll_kind(self):
        total = sum(w for _k, w, _c, _l in TABLE)
        r = random.uniform(0, total)
        acc = 0.0
        for kind, w, _c, _l in TABLE:
            acc += w
            if r <= acc:
                return kind
        return TABLE[-1][0]

    def update(self, dt, players, sound, effects):
        for p in self.pickups:
            p.update(dt)
        # collection
        for p in self.pickups:
            if not p.alive:
                continue
            pr = p.rect()
            for player in players:
                if not player.alive:
                    continue
                prct = pygame.Rect(int(player.x - C.PLAYER_W / 2), int(player.y - C.PLAYER_H / 2),
                                   C.PLAYER_W, C.PLAYER_H)
                if prct.inflate(14, 14).colliderect(pr):
                    p.alive = False
                    self._apply(p.kind, player, sound, effects)
                    break
        self.pickups = [p for p in self.pickups if p.alive]

    def _apply(self, kind, player, sound, effects):
        if kind == "triple":
            player.triple_t = C.TRIPLE_DURATION
            effects.popup(player.x, player.y - 24, "TRIPLE!", C.YELLOW)
            sound.play("powerup")
        elif kind == "rapid":
            player.rapid_t = C.RAPID_DURATION
            effects.popup(player.x, player.y - 24, "RAPID!", C.MAGENTA)
            sound.play("powerup")
        elif kind == "shield":
            player.shield = True
            effects.popup(player.x, player.y - 24, "SHIELD!", C.CYAN)
            sound.play("powerup")
        elif kind == "life":
            player.lives += 1
            effects.popup(player.x, player.y - 24, "1UP!", C.PINK)
            sound.play("extralife")

    def draw(self, surf, font, ox, oy):
        for p in self.pickups:
            p.draw(surf, font, ox, oy)
